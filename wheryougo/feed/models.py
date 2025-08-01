from django.db import models
from django.contrib.auth.models import User
from manage.models import UserProfile

class Post(models.Model):
    POST_TYPES = [
        ('travel', 'Travel Story'),
        ('photo', 'Photo Gallery'),
        ('tip', 'Travel Tip'),
        ('review', 'Review'),
        ('itinerary', 'Itinerary'),
    ]

    POST_CAT = [
        ('story', 'Story'),
        ('photo', 'Photos'),
        ('tip', 'Tip'),
        ('review', 'Review'),
        ('itinerary', 'Itinerary'),
    ]
    
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    
    post_type = models.CharField(max_length=20, choices=POST_TYPES, default='travel')
    
    
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    
    categories = models.CharField(max_length=100, blank=True, help_text="Comma-separated categories (e.g., story,photo)")
    
    tags = models.CharField(max_length=100, blank=True, help_text="Comma-separated tags")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes_count = models.PositiveIntegerField(default=0)
    is_private = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.title} by {self.author.username}"
    
    def get_tags_list(self):
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
    
    def get_categories_list(self):
        return [cat.strip() for cat in self.categories.split(',') if cat.strip()]
    
    def has_photos(self):
        return self.images.exists()
    
    def is_story_with_photos(self):
        cats = self.get_categories_list()
        return 'story' in cats and 'photo' in cats
    
    def get_primary_category(self):
        cats = self.get_categories_list()
        if not cats:
            return 'story'
        return cats[0]
    
class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='posts/')
    caption = models.CharField(max_length=200, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    order = models.PositiveIntegerField(default=1)
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"Image for {self.post.id} user {self.post.author.username}"

class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')
    
    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'post')
    
    def __str__(self):
        return f"{self.user.username} likes {self.post.title}"


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'post')
    
    def __str__(self):
        return f"{self.user.username} favorited {self.post.title}"
    

# Add these comment models after your existing models

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(max_length=500)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')  # For nested comments/replies
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_edited = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['created_at']  # Show oldest first
    
    def __str__(self):
        return f"Comment by {self.author.username} on {self.post.title}"
    
    def is_reply(self):
        """Check if this comment is a reply to another comment"""
        return self.parent is not None
    
    def get_replies(self):
        """Get all replies to this comment"""
        return Comment.objects.filter(parent=self)
    
    def replies_count(self):
        """Count replies to this comment"""
        return self.get_replies().count()

class CommentLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'comment')
    
    def __str__(self):
        return f"{self.user.username} likes comment by {self.comment.author.username}"
    
