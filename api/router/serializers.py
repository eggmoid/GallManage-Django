from rest_framework import serializers

from api.models.post.models import Post


class PostSerializer(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = '__all__'
