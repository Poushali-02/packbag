from django.db import models
from django.contrib.auth.models import User
from datetime import date

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    date_of_birth = models.DateField(null=True, blank=True)
    pfp = models.ImageField(upload_to='profiles/', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=100, blank=True)
    user_type = models.CharField(max_length=20, choices=[
        ('traveler', 'Traveler'),
        ('vlogger', 'Vlogger'),
        ('explorer', 'Explorer'),
        ('wanderer', 'Wanderer')
    ], default='traveler')
    created_at = models.DateTimeField(auto_now_add=True)
    portfolio = models.URLField(max_length=200, blank=True, help_text="Link to your portfolio")
    youtube_channel = models.URLField(max_length=200, blank=True, help_text="Link to your YouTube channel")
    is_private = models.BooleanField(default=False)
    show_location = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.name}"