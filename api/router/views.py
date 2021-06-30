from rest_framework import viewsets

from api.models.post.models import Post

from .serializers import PostSerializer


# Create your views here.
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
