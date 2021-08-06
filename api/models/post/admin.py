from django.contrib import admin
from django.utils.html import format_html

from .models import Post

from server.tasks import save_detail


@admin.action(description='글 내용 저장')
def save_post(modeladmin, request, queryset):
    for q in queryset:
        save_detail.delay(q.num, True)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):

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
        'name',
        'idip',
    ]
    actions = [save_post]

    def get_ordering(self, request):
        return ['-num']
