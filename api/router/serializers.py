from django.db.models.query_utils import select_related_descend
from rest_framework import serializers

from api.models.detail_post.models import DetailPost
from api.models.post.models import Post


class PostSerializer(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = '__all__'


class DetailPostSerializer(serializers.ModelSerializer):

    class Meta:
        model = DetailPost
        fields = ('num',)


class RankSerializer(serializers.Serializer):
    rank = serializers.IntegerField()
    count = serializers.IntegerField()
    name = serializers.CharField()
    idip = serializers.CharField()
    comment_count = serializers.IntegerField()
    gall_count = serializers.IntegerField()
    gall_recommend = serializers.IntegerField()


class RankingSerializer(serializers.Serializer):
    ranking = RankSerializer(many=True)
