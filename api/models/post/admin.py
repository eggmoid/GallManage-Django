from django.contrib import admin

from .models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = [
        'num',
        'title',
        'name',
        'idip',
        'date',
        'comment_count',
        'gall_count',
        'gall_recommend',
    ]
    search_fields = [
        'name',
        'idip',
    ]

    def get_ordering(self, request):
        return ['-num']
