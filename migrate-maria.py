from api.models.post.models import Post

c = Post.objects.count()
ps = Post.objects.order_by('date')[:100]
Post.objects.using('mariadb').bulk_create(ps)

## new shell - mariadb
# update post set newdate=str_to_date(date, '%Y-%m-%d %H:%i:%s');
