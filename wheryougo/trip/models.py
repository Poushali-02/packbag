from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Trip(models.Model):
    name = models.CharField(max_length=50, help_text="Name of the trip, e.g., Bali Trip")
    description = models.TextField(blank=True, help_text="Optional description of the trip")
    created_by = models.ForeignKey(User, default=False,on_delete=models.CASCADE, related_name='created_trips', help_text="User who created the trip")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Date and time when the trip was created")
    start_date = models.DateField(help_text="Start date of the trip")
    end_date = models.DateField(help_text="End date of the trip")
    members = models.ManyToManyField('auth.User', related_name='trips', help_text="Users participating in the trip")
    successful = models.BooleanField(default=False, help_text="Indicates if the trip was successful")
    status = models.CharField(max_length=20, choices=[
        ('planned', 'Planned'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
    ], default='planned', help_text="Current status of the trip")
    image = models.ImageField(upload_to='trips/', null=True, blank=True, help_text="Optional image for the trip")
    
    def __str__(self):
        return f"{self.name} by {self.created_by.username}"
    
    def is_creator(self, user):
        """Check if the given user is the creator of this trip"""
        return self.created_by == user
    
    def is_member(self, user):
        """Check if the given user is a member of this trip"""
        return self.members.filter(id=user.id).exists()
    
    def get_duration_days(self):
        """Calculate the duration of the trip in days"""
        return (self.end_date - self.start_date).days + 1
    
    class Meta:
        ordering = ['-created_at']