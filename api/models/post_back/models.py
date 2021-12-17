from django.db import models


class BPost(models.Model):
    num = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=320)
    name = models.CharField(max_length=120)
    idip = models.CharField(max_length=20)
    date = models.CharField(max_length=19)
    comment_count = models.IntegerField(null=True)
    gall_count = models.IntegerField(null=True)
    gall_recommend = models.IntegerField(null=True)

    class Meta:
        db_table = 'bpost'
        app_label = "mariadb"
        verbose_name = '게시글 (백업) - 검색결과 정렬 금지 (매우 느림)'
        verbose_name_plural = '글 목록 (백업) - 검색결과 정렬 금지 (매우 느림)'
