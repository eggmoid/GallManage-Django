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
