from django.contrib import admin
from django.utils.html import format_html

from .models import BPost


@admin.register(BPost)
class BPostAdmin(admin.ModelAdmin):

    def has_add_permission(self, request, obj=None) -> bool:
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        return False

    def TITLE(self, obj):
        _url = f"https://gall.dcinside.com/mgallery/board/view/?id=girlgroup&no={obj.num}"
        return format_html("<a href='{url}'>{title}</a>",
                           url=_url,
                           title=obj.title)

    list_display = [
        'num',
        'TITLE',
        'name',
        'idip',
        'date',
        'comment_count',
        'gall_count',
        'gall_recommend',
    ]
    search_fields = [
        '=name',
        '=idip',
    ]

    def get_ordering(self, request):
        return ['-num']
