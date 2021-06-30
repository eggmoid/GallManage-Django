from django.conf.urls import include, url
from rest_framework import routers

from .views import (
    PostViewSet,)

router = routers.DefaultRouter(trailing_slash=False)

router.register(r'posts', PostViewSet, basename='post')

urlpatterns = [
    url(r'^', include(router.urls)),
]
