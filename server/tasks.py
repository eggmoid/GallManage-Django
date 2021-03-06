import json
import os
import re
import requests

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')

app = Celery('task')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks


@app.task
def backup_post(_from=None):
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT MAX(NUM) FROM BPOST;")
        max_num = cursor.fetchone()[0]
        if not _from or (int(_from) > int(max_num)):
            cursor.execute(
                f"INSERT INTO BPOST (SELECT * FROM POST WHERE NUM > {max_num});"
            )
        else:
            cursor.execute(f"DELETE FROM BPOST WHERE NUM >= {_from};")
            cursor.execute(
                f"INSERT INTO BPOST (SELECT * FROM POST WHERE NUM >= {_from});")


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
def save_detail(num, refresh=False, ban=False):
    from api.models.detail_post.models import DetailPost
    from api.models.post.models import Post
    # URL = f"https://gall.dcinside.com/mgallery/board/view/?id=girlgroup&no={num}"
    URL = f"https://m.dcinside.com/board/girlgroup/{num}"
    try:
        post = Post.objects.get(num=num)
    except Post.DoesNotExist:
        return False
    _resp = requests.get(
        URL,
        headers={
            "User-Agent":
                "Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1"
        })
    resp = re.sub('<script.*?</script>', '', _resp.text, flags=re.DOTALL)
    resp = re.sub(r'<img src=("?.*?"?).*?data-original="?(.*?)"? ',
                  r'<img src="\2" ', resp)
    resp = re.sub(r'<img src="?https://dcimg\d\.dcinside\.co\.kr(.*?)"? ',
                  r'<img src="https://images.dcinside.com\1" ', resp)
    # resp = re.sub(
    #     r'<img src=("?https://nstatic.dcinside.com/dc/m/img/dccon_loading_nobg200.png"?).*?data-original="?(.*?)"? ',
    #     r'<img src="\2" ',
    #     resp,
    #     flags=re.DOTALL)
    (detail, created) = DetailPost.objects.get_or_create(num=post)
    if created or (refresh and
                   ("/derror/deleted/girlgroup/minor" not in resp) and
                   resp != "" and _resp.status_code == 200):
        detail.detail = resp
        detail.save()
    if ban:
        requests.post("http://localhost:4567/block", data=json.dumps({'no': num}))


@app.task
def sync_gall(page=1, page_end=1):
    from api.models.post.models import Post
    from django.conf import settings
    URL = "https://gall.dcinside.com/mgallery/board/lists/?id=girlgroup&page="
    MONITOR = settings.MONITOR
    try:
        last_num = Post.objects.last().num
    except AttributeError:
        resp = requests.get(f"{URL}{page}",
                            headers={
                                "User-Agent": "Mozilla/5.0"
                            }).text
        source = list(
            map(map_post, re.findall('ub-content.*?</tr>',
                                     resp,
                                     flags=re.DOTALL)))
        last_num = source[0][0]
    resp = requests.get(f"{URL}{page}",
                        headers={
                            "User-Agent": "Mozilla/5.0"
                        }).text
    source = list(
        map(map_post, re.findall('ub-content.*?</tr>',
                                 resp,
                                 flags=re.DOTALL)))
    # source.sort()
    # source.reverse()
    for e in source:
        try:
            post = Post.objects.get(num=e[0])
        except Post.DoesNotExist:
            post = Post(num=e[0])
            post.title = e[1]
            post.name = e[2]
            post.idip = e[3]
            post.date = e[4]
            post.comment_count = e[5]
            post.gall_count = e[6]
            post.gall_recommend = e[7]
            post.save()
            save_detail.delay(e[0], False)
    return


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')


app.conf.beat_schedule = {
    'daytime': {
        'task': 'server.tasks.sync_gall',
        # 'schedule': crontab(minute='*/2', hour='8-23,0'),
        'schedule': 6,
    },
    # 'nignttime': {
    #     'task': 'server.tasks.sync_gall',
    #     'schedule': crontab(minute='*/3', hour='1-7'),
    # },
}
