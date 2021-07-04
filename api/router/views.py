from django.http.response import Http404, HttpResponse
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets

from api.models.detail_post.models import DetailPost
from api.models.post.models import Post
from server.tasks import sync_gall

from .serializers import (
    DetailPostSerializer,
    PostSerializer,
)


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by('-num')
    serializer_class = PostSerializer
    http_method_names = ['get']
    # http_method_names = ['get', 'post']

    def filter_queryset(self, queryset):
        qs = queryset
        name = self.request.GET.get('name')
        idip = self.request.GET.get('idip')
        if name:
            qs = qs.filter(name__contains=name)
        if idip:
            qs = qs.filter(idip__contains=idip)
        return qs

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('name',
                          openapi.IN_QUERY,
                          description='닉네임',
                          type=openapi.TYPE_STRING),
        openapi.Parameter('idip',
                          openapi.IN_QUERY,
                          description='아이디/아이피',
                          type=openapi.TYPE_STRING)
    ])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(auto_schema=None)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class SyncViewSet(viewsets.ViewSet):

    def create(self, request, *args, **kwargs):
        sync_gall.delay()
        return HttpResponse(status=202)


class DetailViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DetailPost.objects.all().order_by('-num')
    serializer_class = DetailPostSerializer

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, pk, *args, **kwargs):
        try:
            post = Post.objects.get(num=pk)
            detail = DetailPost.objects.get(num=post)
        except (Post.DoesNotExist, DetailPost.DoesNotExist):
            raise Http404()
        return HttpResponse(detail.detail)
