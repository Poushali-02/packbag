from rest_framework import serializers
from .models import Post, PostImage, Follow, Like, Favorite, Comment, CommentLike
from manage.models import UserProfile
from django.contrib.auth.models import User

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['name', 'user_type', 'pfp']

class UserSerializer(serializers.ModelSerializer):
    userprofile = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'userprofile']

class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = ['id', 'image', 'caption', 'order']

class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    images = PostImageSerializer(many=True, read_only=True)
    
    title = serializers.CharField(max_length=200)
    content = serializers.CharField()
    location = serializers.CharField(max_length=200, required=False, allow_blank=True)
    is_private = serializers.BooleanField(default=False)
    
    user_has_liked = serializers.SerializerMethodField()
    user_has_favorited = serializers.SerializerMethodField()
    is_following_author = serializers.SerializerMethodField()

    like_count = serializers.SerializerMethodField()
    favorite_count = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    tags_list = serializers.SerializerMethodField()
    categories_list = serializers.SerializerMethodField()
    has_photos = serializers.SerializerMethodField()
    primary_category = serializers.SerializerMethodField()
    

    class Meta:
        model = Post
        fields = [
            'id',
            'author',
            'post_type',
            'title',
            'content',
            'location',
            'categories',
            'tags',
            'is_private',
            'created_at',
            'updated_at',
            'images',
            'user_has_liked',
            'user_has_favorited',
            'is_following_author',
            'like_count',
            'favorite_count',
            'comment_count',
            'tags_list',
            'categories_list',
            'has_photos',
            'primary_category',
        ]

    def get_user_has_liked(self, obj):
        user = self.context.get('request').user
        if not user.is_authenticated:
            return False
        return obj.likes.filter(user=user).exists()

    def get_user_has_favorited(self, obj):
        user = self.context.get('request').user
        if not user.is_authenticated:
            return False
        return obj.favorites.filter(user=user).exists()

    def get_is_following_author(self, obj):
        user = self.context.get('request').user
        if not user.is_authenticated or obj.author == user:
            return None
        return obj.author.following.filter(follower=user).exists()

    def get_like_count(self, obj):
        return obj.likes.count()

    def get_favorite_count(self, obj):
        return obj.favorites.count()

    def get_comment_count(self, obj):
        return obj.comments.count()

    def get_tags_list(self, obj):
        return obj.get_tags_list()

    def get_categories_list(self, obj):
        return obj.get_categories_list()

    def get_has_photos(self, obj):
        return obj.has_photos()

    def get_primary_category(self, obj):
        return obj.get_primary_category()


class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    replies = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    user_has_liked = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = [
            'id',
            'author',
            'content',
            'parent',
            'created_at',
            'updated_at',
            'is_edited',
            'replies',
            'likes_count',
            'user_has_liked',
        ]
        read_only_fields = ['created_at', 'updated_at', 'is_edited']
    
    def get_replies(self, obj):
        if obj.parent is None:  # Only get replies for top-level comments
            replies = obj.get_replies()
            return CommentSerializer(replies, many=True, context=self.context).data
        return []
    
    def get_likes_count(self, obj):
        return obj.likes.count()
    
    def get_user_has_liked(self, obj):
        user = self.context.get('request').user
        if not user.is_authenticated:
            return False
        return obj.likes.filter(user=user).exists()


class CommentLikeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = CommentLike
        fields = ['id', 'user', 'comment', 'created_at']
        read_only_fields = ['created_at']


class LikeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Like
        fields = ['id', 'user', 'post', 'created_at']
        read_only_fields = ['created_at']


class FavoriteSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Favorite
        fields = ['id', 'user', 'post', 'created_at']
        read_only_fields = ['created_at']


class FollowSerializer(serializers.ModelSerializer):
    follower = UserSerializer(read_only=True)
    following = UserSerializer(read_only=True)
    
    class Meta:
        model = Follow
        fields = ['id', 'follower', 'following', 'created_at']
        read_only_fields = ['created_at']