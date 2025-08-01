from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.contrib import messages
from django.core.paginator import Paginator
from manage.models import UserProfile
from feed.models import Post, Follow, Like, Favorite

def profile(request, username=None):
    """Profile view that shows user's profile and posts"""
    if username:
        # Viewing someone else's profile
        profile_user = get_object_or_404(User, username=username)
    else:
        # Viewing own profile (if logged in)
        if not request.user.is_authenticated:
            return redirect('signin')
        profile_user = request.user
    
    # Get or create user profile
    try:
        user_profile = UserProfile.objects.get(user=profile_user)
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(
            user=profile_user,
            name=profile_user.first_name or profile_user.username,
            user_type='traveler'
        )
    
    # Get user's posts (exclude private posts if not own profile)
    posts = Post.objects.filter(author=profile_user)
    if request.user != profile_user:
        posts = posts.filter(is_private=False)
    
    # Pagination for posts
    paginator = Paginator(posts, 12)
    page_number = request.GET.get('page')
    posts_page = paginator.get_page(page_number)
    
    # Get stats
    followers_count = Follow.objects.filter(following=profile_user).count()
    following_count = Follow.objects.filter(follower=profile_user).count()
    posts_count = posts.count()
    
    # Check if current user follows this profile
    is_following = False
    if request.user.is_authenticated and request.user != profile_user:
        is_following = Follow.objects.filter(
            follower=request.user, 
            following=profile_user
        ).exists()
    
    context = {
        'profile_user': profile_user,
        'user_profile': user_profile,
        'posts': posts_page,
        'followers_count': followers_count,
        'following_count': following_count,
        'posts_count': posts_count,
        'is_following': is_following,
        'is_own_profile': request.user == profile_user,
    }
    
    return render(request, 'profiles/profile.html', context)

@login_required
def edit_profile(request, username):
    """Edit user profile"""
    if request.user.username != username:
        messages.error(request, "You can only edit your own profile.")
        return redirect('profile')
    
    user_profile = get_object_or_404(UserProfile, user=request.user)
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        bio = request.POST.get('bio', '').strip()
        location = request.POST.get('location', '').strip()
        user_type = request.POST.get('user_type', 'traveler')
        
        # Handle profile picture upload
        if 'pfp' in request.FILES:
            try:
                # Use get() method which returns single file or None
                uploaded_file = request.FILES.get('pfp')
                if uploaded_file:
                    user_profile.pfp = uploaded_file
            except Exception as e:
                print(f"File upload error: {e}")
                messages.error(request, "Error uploading profile picture.")
        
        user_profile.name = name or request.user.username
        user_profile.bio = bio
        user_profile.location = location
        user_profile.user_type = user_type
        try:
            user_profile.save()
            messages.success(request, "Profile updated successfully!")
        except Exception as e:
            messages.error(request, f"Error saving profile: {str(e)}")
        
        return redirect('profile')

    return render(request, 'profiles/edit_profile.html', {
        'user_profile': user_profile
    })

@login_required
def follow_user(request, username):
    """Follow/unfollow a user via AJAX"""
    if request.method == 'POST':
        user_to_follow = get_object_or_404(User, username=username)
        
        if user_to_follow != request.user:
            follow, created = Follow.objects.get_or_create(
                follower=request.user,
                following=user_to_follow
            )
            
            if not created:
                # Unfollow
                follow.delete()
                following = False
                action = 'unfollowed'
            else:
                # Follow
                following = True
                action = 'followed'
            
            # Get updated counts
            followers_count = Follow.objects.filter(following=user_to_follow).count()
            
            return JsonResponse({
                'success': True,
                'following': following,
                'action': action,
                'followers_count': followers_count
            })
    
    return JsonResponse({'error': 'Invalid request'}, status=400)