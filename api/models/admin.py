from django.contrib import admin
from django.contrib.auth.models import (
    User,
    Group,
)

admin.site.unregister(User)
admin.site.unregister(Group)

admin.site.site_header = '관계자외 출입금지'
admin.site.site_title = '통제구역'
admin.site.index_title = '목록'
