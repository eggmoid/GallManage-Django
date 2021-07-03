from django.contrib import admin

from .models import DetailPost


@admin.register(DetailPost)
class DetailPostAdmin(admin.ModelAdmin):

    def title(self, obj):
        return obj.num.title

    def name(self, obj):
        return obj.num.name

    def idip(self, obj):
        return obj.num.idip

    def date(self, obj):
        return obj.num.date

    list_display = [
        'num',
        'title',
        'name',
        'idip',
        'date',
    ]
    search_fields = [
        'name',
        'idip',
    ]

    def get_ordering(self, request):
        return ['-num']
