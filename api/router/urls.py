from django.conf.urls import include, url
from rest_framework import routers

from .views import (
    BackupViewSet,
    DetailViewSet,
    KeywordViewSet,
    PostViewSet,
    RankingViewSet,
    SyncViewSet,
)

router = routers.DefaultRouter(trailing_slash=False)

router.register(r'backup', BackupViewSet, basename='backup')
router.register(r'detail', DetailViewSet, basename='detail')
router.register(r'keywords', KeywordViewSet, basename='keyword')
router.register(r'posts', PostViewSet, basename='post')
router.register(r'ranking', RankingViewSet, basename='ranking')
router.register(r'sync', SyncViewSet, basename='sync')

urlpatterns = [
    url(r'^', include(router.urls)),
]
