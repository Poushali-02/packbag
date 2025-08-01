from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from manage.models import UserProfile
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import logout
from .models import Post, Follow, Like, Favorite, PostImage


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
    
    return render(request, 'feed/feed.html', {'user_profile': user_profile})
  
@login_required
def create_post(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(
            user=request.user,
            name=request.user.first_name or request.user.username,
            user_type='traveler'
        )
    
    if request.method == 'POST':
        try:
            post_type = request.POST.get('post_type')
            title = request.POST.get('title')
            content = request.POST.get('content')
            location = request.POST.get('location')
            categories = request.POST.get('categories')
            tags = request.POST.get('tags')
            is_private = request.POST.get('is_private') == 'true'
            privacy = request.POST.get('privacy', 'public')
            is_private = (privacy == 'private')
            
            print(f"DEBUG: Received form data:")
            print(f"  - post_type: {post_type}")
            print(f"  - title: {title}")
            print(f"  - content: {content}")
            print(f"  - privacy: {privacy}")
            print(f"  - is_private: {is_private}")
            print(f"  - uploaded_images count: {len(request.FILES.getlist('uploaded_images'))}")
            
            
            errors = []

            if not title:
                errors.append("Title is required.")
            if not content:
                errors.append("Content is required.")
            # if not location:
            #     errors.append("Location is required.")
            # if not categories:
            #     errors.append("Categories are required.")
            # if not tags:
            #     errors.append("Tags are required.")

            if errors:
                return render(request, 'feed/create_post.html', {
                    'user_profile': user_profile,
                    'errors': errors,
                    'form_data': request.POST
                })
            post = Post.objects.create(
                author=request.user,
                post_type=post_type,
                title=title,
                content=content,
                location=location,
                categories=categories,
                tags=tags,
                is_private=is_private
            )
            uploaded_images = request.FILES.getlist('uploaded_images')
            image_captions = request.POST.getlist('image_captions[]')
            
            print(f"DEBUG: Created post with ID: {post.id}")
            print(f"DEBUG: Processing {len(uploaded_images)} images")
            
            while len(image_captions) < len(uploaded_images):
                image_captions.append('')
            
            for i, image in enumerate(uploaded_images):
                if image:
                    # Validate image
                    if not image.content_type.startswith('image/'):
                        messages.warning(request, f'Skipped non-image file: {image.name}')
                        continue
                    
                    if image.size > 10 * 1024 * 1024:  # 10MB limit
                        messages.warning(request, f'Skipped large image: {image.name} (must be under 10MB)')
                        continue
                    
                    # Create PostImage
                    PostImage.objects.create(
                        post=post,
                        image=image,
                        caption=image_captions[i] if i < len(image_captions) else '',
                        order=i + 1
                    )
            
            messages.success(request, 'Your post has been created successfully!')
            return redirect('profile')
            
        except Exception as e:
            messages.error(request, f'Error creating post: {str(e)}')
            return render(request, 'feed/create_post.html', {
                'user_profile': user_profile,
                'form_data': request.POST
            })
    
    # GET request - show the form
    return render(request, 'feed/create_post.html', {
        'user_profile': user_profile,
        'post_types': Post.POST_TYPES,
    })
    
    
@login_required
def ajax_upload_image(request):
    """Handle AJAX image upload for preview"""
    if request.method == 'POST' and 'image' in request.FILES:
        try:
            image = request.FILES['image']
            
            # Validate image
            if not image.content_type.startswith('image/'):
                return JsonResponse({
                    'success': False,
                    'error': 'Please upload a valid image file.'
                })
            
            if image.size > 10 * 1024 * 1024:  # 10MB limit
                return JsonResponse({
                    'success': False,
                    'error': 'Image file too large. Maximum size is 10MB.'
                })
            
            return JsonResponse({
                'success': True,
                'filename': image.name,
                'size': image.size
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Upload error: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'error': 'No image provided'})

@login_required
def get_tag_suggestions(request):
    """Get popular tags for autocomplete"""
    query = request.GET.get('q', '').lower()
    
    # Get popular tags from existing posts
    popular_tags = [
        'travel', 'adventure', 'backpacking', 'solo', 'budget', 'luxury',
        'beach', 'mountain', 'city', 'nature', 'photography', 'food',
        'culture', 'history', 'wildlife', 'roadtrip', 'europe', 'asia',
        'america', 'africa', 'oceania', 'family', 'friends', 'couple'
    ]
    
    if query:
        suggestions = [tag for tag in popular_tags if query in tag]
    else:
        suggestions = popular_tags[:10]  # Show top 10
    
    return JsonResponse({'suggestions': suggestions})