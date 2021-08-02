import datetime

from api.models.post.models import Post


class PostRank(Post):

    class Meta:
        month = datetime.datetime.today().month
        proxy = True
        verbose_name = f'{datetime.datetime.today().month}월 갤창랭킹'
        verbose_name_plural = f'{datetime.datetime.today().month}월 갤창랭킹'
