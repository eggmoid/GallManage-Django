from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import DetailPost


@admin.register(DetailPost)
class DetailPostAdmin(admin.ModelAdmin):

    def has_add_permission(self, request, obj=None) -> bool:
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        if request.user.username == 'admin':
            return True
        return False

    def log_deletion(self, request, object, message):
        # return super().log_addition(request, object, message)
        return

    def NUM(self, obj):
        _cache = reverse('detail-detail', args=[obj.num.num])
        return format_html("<a href='{url}'>{num}</a>",
                           url=_cache,
                           num=obj.num.num)

    def title(self, obj):
        _url = f"https://gall.dcinside.com/mgallery/board/view/?id=girlgroup&no={obj.num.num}"
        return format_html("<a href='{url}'>{title}</a>",
                           url=_url,
                           title=obj.num.title)

    def name(self, obj):
        return obj.num.name

    def idip(self, obj):
        return obj.num.idip

    def date(self, obj):
        return obj.num.date

    def url(self, obj):
        _url = f"https://gall.dcinside.com/mgallery/board/view/?id=girlgroup&no={obj.num.num}"
        return format_html("<a href='{url}'>LINK</a>", url=_url)

    def cache(self, obj):
        _cache = reverse('detail-detail', args=[obj.num.num])
        return format_html("<a href='{url}'>CACHE</a>", url=_cache)

    list_display = [
        'NUM',
        'title',
        'name',
        'idip',
        'date',
        'url',
        'cache',
    ]
    search_fields = [
        'num__name',
        'num__idip',
    ]

    def get_ordering(self, request):
        return ['-num']
