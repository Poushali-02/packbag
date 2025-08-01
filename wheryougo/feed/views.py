from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from manage.models import UserProfile
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import logout


# Create your views here.
@login_required(login_url='manage/signin')
def feed(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        # Create a UserProfile if it doesn't exist
        user_profile = UserProfile.objects.create(
            user=request.user,
            name=request.user.first_name or request.user.username,
            user_type='traveler'  # Default user type
        )
        messages.info(request, 'Welcome! Your profile has been created.')
    
    return render(request, 'website/feed.html', {'user_profile': user_profile})
  