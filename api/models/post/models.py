from django.db import models


class Post(models.Model):
    num = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=320)
    name = models.CharField(max_length=120)
    idip = models.CharField(max_length=20)
    date = models.DateTimeField(null=True)
    comment_count = models.IntegerField(null=True)
    gall_count = models.IntegerField(null=True)
    gall_recommend = models.IntegerField(null=True)

    class Meta:
        db_table = 'post'
        verbose_name = '게시글'
        verbose_name_plural = '글 목록'
