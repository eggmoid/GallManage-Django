from api.models.post.models import Post


class PostRank(Post):

    class Meta:
        proxy = True
        verbose_name = '7월 갤창랭킹'
        verbose_name_plural = '7월 갤창랭킹'
