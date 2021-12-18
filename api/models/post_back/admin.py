from django.contrib import admin
from django.utils.html import format_html

from .models import BPost


@admin.register(BPost)
class BPostAdmin(admin.ModelAdmin):
    using = 'mongodb'

    def save_model(self, request, obj, form, change):
        # Tell Django to save objects to the 'other' database.
        obj.save(using=self.using)

    def delete_model(self, request, obj):
        # Tell Django to delete objects from the 'other' database
        obj.delete(using=self.using)

    def get_queryset(self, request):
        # Tell Django to look for objects on the 'other' database.
        return super().get_queryset(request).using(self.using)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Tell Django to populate ForeignKey widgets using a query
        # on the 'other' database.
        return super().formfield_for_foreignkey(db_field,
                                                request,
                                                using=self.using,
                                                **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        # Tell Django to populate ManyToMany widgets using a query
        # on the 'other' database.
        return super().formfield_for_manytomany(db_field,
                                                request,
                                                using=self.using,
                                                **kwargs)

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
