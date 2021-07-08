from django.conf.urls import include, url
from rest_framework import routers

from .views import (
    DetailViewSet,
    PostViewSet,
    RankingViewSet,
    SyncViewSet,
)

router = routers.DefaultRouter(trailing_slash=False)

router.register(r'detail', DetailViewSet, basename='detail')
router.register(r'posts', PostViewSet, basename='post')
router.register(r'ranking', RankingViewSet, basename='ranking')
router.register(r'sync', SyncViewSet, basename='sync')

urlpatterns = [
    url(r'^', include(router.urls)),
]
