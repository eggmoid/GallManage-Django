import os
import re
import requests

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')

app = Celery('task')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks


def map_post(e: str):
    num = int((re.findall(r'no=(\d+)', e) or [0])[0])
    title = (re.findall(r'</em>(.*?)</a>', e) or [""])[0]
    name = (re.findall(r'data-nick="(.*?)"', e) or [""])[0]
    id = (re.findall(r'data-uid="(.*?)"', e) or [""])[0]
    ip = (re.findall(r'data-ip="(.*?)"', e) or [""])[0]
    idip = id + ip
    date = (re.findall(r'gall_date" title="(.*?)"', e) or [""])[0]
    comment_count = int((re.findall(r'reply_num">\[(\d*?)\]', e) or [0])[0])
    gall_count = int((re.findall(r'gall_count">(\d*?)<', e) or [0])[0])
    gall_recommend = int((re.findall(r'gall_recommend">(\d*?)<', e) or [0])[0])
    return [
        num, title, name, idip, date, comment_count, gall_count, gall_recommend
    ]


@app.task
def sync_gall():
    from api.models.post.models import Post
    page = 1
    URL = "https://gall.dcinside.com/mgallery/board/lists/?id=girlgroup&page="
    last_num = Post.objects.last().num
    while True:
        resp = requests.get(f"{URL}{page}",
                            headers={
                                "User-Agent": "Mozilla/5.0"
                            }).text
        source = list(
            map(map_post, re.findall('ub-content.*?</tr>',
                                     resp,
                                     flags=re.DOTALL)))
        if not len([e for e in source if e[0] > last_num]):
            return
        for e in source:
            (post, created) = Post.objects.get_or_create(num=e[0])
            post.title = e[1]
            post.name = e[2]
            post.idip = e[3]
            post.date = e[4]
            post.comment_count = e[5]
            post.gall_count = e[6]
            post.gall_recommend = e[7]
            post.save()
        page += 1


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')


app.conf.beat_schedule = {
    'add-every-5-minutes-crontab': {
        'task': 'server.tasks.sync_gall',
        'schedule': crontab(minute='*/5'),
    },
}
