from django.db.models import Count, Sum
from django.http.response import Http404, HttpResponse, JsonResponse
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAdminUser

from api.models.detail_post.models import DetailPost
from api.models.post.models import Post
from server.settings import MONITOR
from server.tasks import (
    backup_post,
    sync_gall,
)

from .serializers import (
    BackupSerializer,
    DetailPostSerializer,
    KeywordSerializer,
    PostSerializer,
    RankingSerializer,
)


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by('-num')
    serializer_class = PostSerializer
    http_method_names = ['get']

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


class BackupViewSet(viewsets.ViewSet):

    @swagger_auto_schema(request_body=BackupSerializer)
    def create(self, request, *args, **kwargs):
        serializer = BackupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        _from = serializer.data.get('_from')
        # to = serializer.data.get('to')
        backup_post.delay(_from)
        return HttpResponse(status=202)


class SyncViewSet(viewsets.ViewSet):

    def create(self, request, *args, **kwargs):
        sync_gall.delay()
        return HttpResponse(status=202)


class DetailViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DetailPost.objects.all().order_by('-num')
    serializer_class = DetailPostSerializer
    permission_classes = (AllowAny,)

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, pk, *args, **kwargs):
        try:
            post = Post.objects.get(num=pk)
            detail = DetailPost.objects.get(num=post)
        except (Post.DoesNotExist, DetailPost.DoesNotExist):
            raise Http404()
        return HttpResponse(detail.detail)


class RankingViewSet(viewsets.ViewSet):

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('date',
                          openapi.IN_QUERY,
                          description='날짜 ex.2021-07',
                          type=openapi.TYPE_STRING),
        openapi.Parameter('num',
                          openapi.IN_QUERY,
                          description='최대 순위',
                          type=openapi.TYPE_INTEGER)
    ],
                         responses={200: RankingSerializer})
    def list(self, request, *args, **kwargs):
        date = request.GET.get('date', "2021-07")
        num = int(request.GET.get('num', 20))
        queryset = Post.objects.filter(date__startswith=date).values_list(
            'name',
            'idip').annotate(comment_count=Sum('comment_count')).annotate(
                gall_count=Sum('gall_count')).annotate(
                    gall_recommend=Sum('gall_recommend')).annotate(
                        count=Count('*')).order_by('-count')[:num]
        resp = {
            "result": [{
                "rank": idx + 1,
                "count": q[-1],
                "name": q[0],
                "idip": q[1],
                "comment_count": q[2],
                "gall_count": q[3],
                "gall_recommend": q[4],
            } for idx, q in enumerate(queryset)]
        }
        return JsonResponse(resp)


class KeywordViewSet(viewsets.ViewSet):
    permission_classes = (IsAdminUser,)

    @swagger_auto_schema(responses={200: KeywordSerializer})
    def list(self, request, *args, **kwargs):
        MONITOR_TITLE = [
            title.decode('utf-8') for title in MONITOR.sdiff('TITLE')
        ]
        return JsonResponse({'keyword': MONITOR_TITLE})

    @swagger_auto_schema(request_body=KeywordSerializer)
    def create(self, request, *args, **kwargs):
        serializer = KeywordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        for keyword in serializer.data['keyword']:
            MONITOR.sadd('TITLE', keyword)
        return HttpResponse(status=201)

    def destroy(self, request, pk, *args, **kwargs):
        MONITOR.srem('TITLE', pk)
        return HttpResponse(status=204)
