import datetime

from django.contrib import admin
from django.db.models import Count, Sum

from .models import PostRank


@admin.register(PostRank)
class PostRankAdmin(admin.ModelAdmin):
    change_list_template = 'admin/summary.html'

    def has_add_permission(self, request, obj=None) -> bool:
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        return False

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(
            request,
            extra_context=extra_context,
        )

        try:
            qs = response.context_data['cl'].queryset
        except (AttributeError, KeyError):
            return response

        metrics = {
            'comment_count': Sum('comment_count'),
            'gall_count': Sum('gall_count'),
            'gall_recommend': Sum('gall_recommend'),
            'count': Count('*')
        }

        _order = request.GET.get('o')
        if _order == '4':
            order = '-comment_count'
        elif _order == '5':
            order = '-gall_count'
        elif _order == '6':
            order = '-gall_recommend'
        else:
            order = '-count'

        response.context_data['summary'] = [{
            "rank": idx + 1,
            "count": q[-1],
            "name": q[0],
            "idip": q[1],
            "comment_count": q[2],
            "gall_count": q[3],
            "gall_recommend": q[4],
        } for idx, q in enumerate(
            qs.filter(date__startswith=datetime.datetime.today().strftime(
                "%Y-%m")).values_list('name', 'idip').annotate(
                    **metrics).order_by(order))]

        return response
