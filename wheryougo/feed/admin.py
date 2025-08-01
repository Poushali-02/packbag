from django.contrib import admin
from .models import Post, PostImage, Comment, CommentLike, Like, Favorite, Follow
# Register your models here.
admin.site.register(Post)
admin.site.register(PostImage)
admin.site.register(Comment)
admin.site.register(CommentLike)
admin.site.register(Like)
admin.site.register(Favorite)
admin.site.register(Follow)