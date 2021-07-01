from django.conf.urls import include, url
from rest_framework import routers

from .views import (
    PostViewSet,
    SyncViewSet,
)

router = routers.DefaultRouter(trailing_slash=False)

router.register(r'posts', PostViewSet, basename='post')
router.register(r'sync', SyncViewSet, basename='sync')

urlpatterns = [
    url(r'^', include(router.urls)),
]
