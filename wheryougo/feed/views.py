from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from manage.models import UserProfile
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import logout
from django.db.models import Q, Count
from django.core.paginator import Paginator
from .models import Post, Follow, Like, Favorite, PostImage, CommentLike, Comment


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
    
    
    following_users = Follow.objects.filter(follower=request.user).values_list('following', flat=True)
    posts = Post.objects.filter(
        Q(author__in=following_users) | Q(author=request.user),
        is_private=False  # Only public posts in feed
    ).select_related('author').prefetch_related(
        'images', 'author__userprofile'
    ).annotate(
        total_likes=Count('likes', distinct=True),
        total_favorites=Count('favorites', distinct=True),
        comment_count = Count('comments', distinct=True)
    ).order_by('-created_at')
    
    if not posts.exists():
        posts = Post.objects.filter(
            is_private=False
        ).select_related('author').prefetch_related(
            'images', 'author__userprofile'
        ).annotate(
            total_likes=Count('likes', distinct=True),
            total_favorites=Count('favorites', distinct=True)
        ).order_by('-created_at', '-total_likes')[:20]
    
    # Create lists of liked and favorited post IDs for template
    user_liked_posts = list(Like.objects.filter(user=request.user).values_list('post_id', flat=True))
    user_favorited_posts = list(Favorite.objects.filter(user=request.user).values_list('post_id', flat=True))
    
    for post in posts:
        post.user_has_liked = Like.objects.filter(user=request.user, post=post).exists()
        post.user_has_favorited = Favorite.objects.filter(user=request.user, post=post).exists()
        post.is_following_author = Follow.objects.filter(
            follower=request.user, 
            following=post.author
        ).exists() if post.author != request.user else None
        
        # Add dynamic properties for template
        post.like_count = post.total_likes
        post.favorite_count = post.total_favorites
        post.comment_count = 0
        post.tags_list = post.get_tags_list()
    
    paginator = Paginator(posts, 10)  # 10 posts per page
    page_number = request.GET.get('page')
    posts_page = paginator.get_page(page_number)
    
    suggested_users = User.objects.exclude(
        id__in=following_users
    ).exclude(
        id=request.user.id
    ).select_related('userprofile').annotate(
        followers_count=Count('following')
    ).order_by('-followers_count')[:5]
    
    context = {
        'user_profile': user_profile,
        'posts': posts_page,
        'suggested_users': suggested_users,
        'following_count': following_users.count() if following_users else 0,
        'user_liked_posts': user_liked_posts,
        'user_favorited_posts': user_favorited_posts,
    }
    return render(request, 'feed/feed.html', context)
  
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

@login_required
def toggle_like(request, post_id):
    if request.method == "POST":
        post = get_object_or_404(Post, id=post_id)
        liked = Like.objects.filter(user=request.user, post=post).first()
        if liked:
            liked.delete()
            liked_status = False
        else:
            Like.objects.create(user=request.user, post=post)
            liked_status = True
        like_count = Like.objects.filter(post=post).count()
        return JsonResponse({'success': True, 'liked': liked_status, 'like_count': like_count})
    return JsonResponse({'success': False}, status=400)

@login_required
def toggle_favourite(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, id=post_id)
        favourite = Favorite.objects.filter(user=request.user, post=post).first()
        if favourite:
            favourite.delete()
            favourite_status = False
        else:
            Favorite.objects.create(user=request.user, post=post)
            favourite_status=True
        favourite_count = Favorite.objects.filter(post=post).count()
        return JsonResponse({'success': True, 'favourited': favourite_status, 'favourite_count': favourite_count})
    return JsonResponse({'success': False}, status=400)

@login_required
def toggle_comment_like(request, comment_id):
    if request.method == 'POST':
        comment = get_object_or_404(CommentLike, id=comment_id)
        comment_like = CommentLike.objects.filter(user=request.user,comment=comment).first()
        if comment_like:
            comment_like.delete()
            comment_like_status = False
        else:
            CommentLike.objects.create(user=request.user, comment=comment)
            comment_like_status=True
        comment_like_count = CommentLike.objects.filter(comment=comment).count()
        return JsonResponse({'success': True, 'liked': comment_like_status, 'like_count': comment_like_count})
    return JsonResponse({'success': False}, status=400)

@login_required
def view_post(request, post_id):
    post = get_object_or_404(Post.objects.prefetch_related('images', 'likes__user', 'comments__author'), id=post_id)
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to comment.")
            return redirect('signin')
        
        content = request.POST.get('comment', '').strip()
        if content:
            Comment.objects.create(post=post, author=request.user, content=content)
            messages.success(request, "Comment added!")
            return redirect('view_post', post_id=post.id)
        else:
            messages.error(request, "Comment cannot be empty.")

    return render(request, 'feed/_post.html', {'post': post})

@login_required
def comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to comment.")
            return redirect('signin')
        
        content = request.POST.get('comment', '').strip()
        if content:
            Comment.objects.create(post=post, author=request.user, content=content)
            messages.success(request, "Comment added!")
            return redirect('view_post', post_id=post.id)
        else:
            messages.error(request, "Comment cannot be empty.")
    
    return render(request, 'feed/_post.html', {'post': post})