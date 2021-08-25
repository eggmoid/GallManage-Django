import datetime

from api.models.post.models import Post

MONTH = (datetime.datetime.today() - datetime.timedelta(days=5)).month


class PostRank(Post):

    class Meta:
        proxy = True
        verbose_name = f'{MONTH}월 갤창랭킹'
        verbose_name_plural = f'{MONTH}월 갤창랭킹'
