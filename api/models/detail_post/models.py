from django.db import models

from api.models.post.models import Post


class DetailPost(models.Model):
    num = models.OneToOneField(Post,
                               unique=True,
                               primary_key=True,
                               on_delete=models.DO_NOTHING,
                               related_name='detail',
                               db_column='num')
    detail = models.TextField()

    class Meta:
        db_table = 'detail_post'
