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
from notification.models import Notification
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework import status
from .serializers import (
    PostSerializer, CommentSerializer, UserSerializer, 
    LikeSerializer, FavoriteSerializer, FollowSerializer,
    CommentLikeSerializer, PostImageSerializer
)


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
    users = User.objects.select_related('userprofile')[:10]

    posts = Post.objects.filter(
        Q(author__in=users) | Q(author=request.user),
        is_private=False
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
        post.comment_count = post.comments.count
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
    ).order_by('-followers_count')[:3]
    
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
            Notification.objects.filter(
                to_user=post.author,
                from_user=request.user,
                notif_type='like',
                post=post
            ).delete()
        else:
            Like.objects.create(user=request.user, post=post)
            liked_status = True
            
            if post.author != request.user:
                Notification.objects.create(
                    to_user=post.author,
                    from_user=request.user,
                    notification_type='like',
                    post=post
                )

        like_count = Like.objects.filter(post=post).count()
        return JsonResponse({'success': True, 'liked': liked_status, 'like_count': like_count})
    return JsonResponse({'success': False}, status=400)

@login_required
def toggle_favorite(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, id=post_id)
        favorite = Favorite.objects.filter(user=request.user, post=post).first()
        if favorite:
            favorite.delete()
            favorite_status = False
        else:
            Favorite.objects.create(user=request.user, post=post)
            favorite_status=True

            if post.author != request.user:
                Notification.objects.create(
                    to_user=post.author,
                    from_user=request.user,
                    notification_type='favorite',
                    post=post
                )
        favorite_count = Favorite.objects.filter(post=post).count()
        return JsonResponse({'success': True, 'favorited': favorite_status, 'favorite_count': favorite_count})
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
            if post.author != request.user:
                Notification.objects.create(
                    to_user=post.author,
                    from_user=request.user,
                    notification_type='comment',
                    post=post
                )
            
            return redirect('view_post', post_id=post.id)
        else:
            messages.error(request, "Comment cannot be empty.")
    
    return render(request, 'feed/_post.html', {'post': post})


# ============= API VIEWS FOR FRONTEND =============

@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def api_feed(request):
    """
    Get feed posts with all necessary data for frontend
    """
    try:
        # Get following users for the authenticated user
        if request.user.is_authenticated:
            following_users = Follow.objects.filter(follower=request.user).values_list('following', flat=True)
            users = User.objects.select_related('userprofile')[:10]
            
            # Get posts from following users and user's own posts
            posts = Post.objects.filter(
                Q(author__in=users) | Q(author=request.user),
                is_private=False
            ).select_related('author').prefetch_related(
                'images', 'author__userprofile', 'likes', 'favorites', 'comments'
            ).annotate(
                total_likes=Count('likes', distinct=True),
                total_favorites=Count('favorites', distinct=True),
                comment_count=Count('comments', distinct=True)
            ).order_by('-created_at')
            
            # If no posts from following users, get popular posts
            if not posts.exists():
                posts = Post.objects.filter(
                    is_private=False
                ).select_related('author').prefetch_related(
                    'images', 'author__userprofile', 'likes', 'favorites', 'comments'
                ).annotate(
                    total_likes=Count('likes', distinct=True),
                    total_favorites=Count('favorites', distinct=True),
                    comment_count=Count('comments', distinct=True)
                ).order_by('-created_at', '-total_likes')[:20]
                
        else:
            # For anonymous users, show public posts only
            posts = Post.objects.filter(
                is_private=False
            ).select_related('author').prefetch_related(
                'images', 'author__userprofile', 'likes', 'favorites', 'comments'
            ).annotate(
                total_likes=Count('likes', distinct=True),
                total_favorites=Count('favorites', distinct=True),
                comment_count=Count('comments', distinct=True)
            ).order_by('-created_at')[:20]
        
        # Pagination
        paginator = Paginator(posts, 10)
        page_number = request.GET.get('page', 1)
        posts_page = paginator.get_page(page_number)
        
        # Serialize posts
        serializer = PostSerializer(posts_page, many=True, context={'request': request})
        
        # Get suggested users
        suggested_users = []
        if request.user.is_authenticated:
            suggested_users_qs = User.objects.exclude(
                id__in=following_users if 'following_users' in locals() else []
            ).exclude(
                id=request.user.id
            ).select_related('userprofile').annotate(
                followers_count=Count('following')
            ).order_by('-followers_count')[:5]
            
            suggested_users = UserSerializer(suggested_users_qs, many=True, context={'request': request}).data
        
        return Response({
            'posts': serializer.data,
            'suggested_users': suggested_users,
            'pagination': {
                'current_page': posts_page.number,
                'total_pages': paginator.num_pages,
                'has_next': posts_page.has_next(),
                'has_previous': posts_page.has_previous(),
                'total_posts': paginator.count
            },
            'user_authenticated': request.user.is_authenticated,
            'following_count': following_users.count() if request.user.is_authenticated and 'following_users' in locals() else 0
        })
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_create_post(request):
    """
    Create a new post via API
    """
    try:
        # Get or create user profile
        try:
            user_profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            user_profile = UserProfile.objects.create(
                user=request.user,
                name=request.user.first_name or request.user.username,
                user_type='traveler'
            )
        
        # Create post
        post_data = {
            'post_type': request.data.get('post_type', 'travel'),
            'title': request.data.get('title'),
            'content': request.data.get('content'),
            'location': request.data.get('location', ''),
            'categories': request.data.get('categories', ''),
            'tags': request.data.get('tags', ''),
            'is_private': request.data.get('is_private', False)
        }
        
        # Validate required fields
        if not post_data['title']:
            return Response({'error': 'Title is required'}, status=status.HTTP_400_BAD_REQUEST)
        if not post_data['content']:
            return Response({'error': 'Content is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create post
        post = Post.objects.create(
            author=request.user,
            **post_data
        )
        
        # Handle image uploads
        uploaded_images = request.FILES.getlist('images')
        image_captions = request.data.getlist('image_captions')
        
        # Ensure captions list matches images list
        while len(image_captions) < len(uploaded_images):
            image_captions.append('')
        
        for i, image in enumerate(uploaded_images):
            if image:
                # Validate image
                if not image.content_type.startswith('image/'):
                    continue
                
                if image.size > 10 * 1024 * 1024:  # 10MB limit
                    continue
                
                PostImage.objects.create(
                    post=post,
                    image=image,
                    caption=image_captions[i] if i < len(image_captions) else '',
                    order=i + 1
                )
        
        # Return serialized post
        serializer = PostSerializer(post, context={'request': request})
        return Response({
            'message': 'Post created successfully',
            'post': serializer.data
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def api_get_post(request, post_id):
    """
    Get a single post with all details
    """
    try:
        post = get_object_or_404(
            Post.objects.prefetch_related(
                'images', 'likes__user', 'comments__author', 'favorites__user'
            ), 
            id=post_id
        )
        
        # Check privacy
        if post.is_private and request.user != post.author:
            return Response({
                'error': 'Post not found or private'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = PostSerializer(post, context={'request': request})
        
        # Get comments for this post
        comments = Comment.objects.filter(post=post).select_related('author').prefetch_related('likes')
        comments_serializer = CommentSerializer(comments, many=True, context={'request': request})
        
        return Response({
            'post': serializer.data,
            'comments': comments_serializer.data
        })
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_toggle_like(request, post_id):
    """
    Toggle like on a post
    """
    try:
        post = get_object_or_404(Post, id=post_id)
        liked = Like.objects.filter(user=request.user, post=post).first()
        
        if liked:
            liked.delete()
            liked_status = False
            # Remove notification
            Notification.objects.filter(
                to_user=post.author,
                from_user=request.user,
                notification_type='like',
                post=post
            ).delete()
        else:
            Like.objects.create(user=request.user, post=post)
            liked_status = True
            
            # Create notification
            if post.author != request.user:
                Notification.objects.create(
                    to_user=post.author,
                    from_user=request.user,
                    notification_type='like',
                    post=post
                )
        
        like_count = post.likes.count()
        
        return Response({
            'success': True,
            'liked': liked_status,
            'like_count': like_count
        })
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_toggle_favorite(request, post_id):
    """
    Toggle favorite on a post
    """
    try:
        post = get_object_or_404(Post, id=post_id)
        favorite = Favorite.objects.filter(user=request.user, post=post).first()
        
        if favorite:
            favorite.delete()
            favorite_status = False
        else:
            Favorite.objects.create(user=request.user, post=post)
            favorite_status = True
            
            # Create notification
            if post.author != request.user:
                Notification.objects.create(
                    to_user=post.author,
                    from_user=request.user,
                    notification_type='favorite',
                    post=post
                )
        
        favorite_count = post.favorites.count()
        
        return Response({
            'success': True,
            'favorited': favorite_status,
            'favorite_count': favorite_count
        })
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_add_comment(request, post_id):
    """
    Add a comment to a post
    """
    try:
        post = get_object_or_404(Post, id=post_id)
        content = request.data.get('content', '').strip()
        parent_id = request.data.get('parent_id')
        
        if not content:
            return Response({
                'error': 'Comment content is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if parent comment exists (for replies)
        parent_comment = None
        if parent_id:
            parent_comment = get_object_or_404(Comment, id=parent_id, post=post)
        
        comment = Comment.objects.create(
            post=post,
            author=request.user,
            content=content,
            parent=parent_comment
        )
        
        # Create notification
        if post.author != request.user:
            Notification.objects.create(
                to_user=post.author,
                from_user=request.user,
                notification_type='comment',
                post=post
            )
        
        serializer = CommentSerializer(comment, context={'request': request})
        
        return Response({
            'success': True,
            'comment': serializer.data,
            'message': 'Comment added successfully'
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_toggle_comment_like(request, comment_id):
    """
    Toggle like on a comment
    """
    try:
        comment = get_object_or_404(Comment, id=comment_id)
        comment_like = CommentLike.objects.filter(user=request.user, comment=comment).first()
        
        if comment_like:
            comment_like.delete()
            liked_status = False
        else:
            CommentLike.objects.create(user=request.user, comment=comment)
            liked_status = True
        
        like_count = comment.likes.count()
        
        return Response({
            'success': True,
            'liked': liked_status,
            'like_count': like_count
        })
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def api_get_tag_suggestions(request):
    """
    Get tag suggestions for autocomplete
    """
    query = request.GET.get('q', '').lower()
    
    # Popular travel tags
    popular_tags = [
        'travel', 'adventure', 'backpacking', 'solo', 'budget', 'luxury',
        'beach', 'mountain', 'city', 'nature', 'photography', 'food',
        'culture', 'history', 'wildlife', 'roadtrip', 'europe', 'asia',
        'america', 'africa', 'oceania', 'family', 'friends', 'couple',
        'hiking', 'camping', 'hotel', 'hostel', 'restaurant', 'museum',
        'sunset', 'sunrise', 'landscape', 'street', 'architecture'
    ]
    
    if query:
        suggestions = [tag for tag in popular_tags if query in tag]
    else:
        suggestions = popular_tags[:10]
    
    return Response({
        'suggestions': suggestions
    })


@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def api_search_posts(request):
    """
    Search posts by title, content, tags, or location
    """
    try:
        query = request.GET.get('q', '').strip()
        post_type = request.GET.get('type', '')
        location = request.GET.get('location', '')
        tags = request.GET.get('tags', '')
        
        posts = Post.objects.filter(is_private=False)
        
        if query:
            posts = posts.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query) |
                Q(tags__icontains=query) |
                Q(location__icontains=query)
            )
        
        if post_type:
            posts = posts.filter(post_type=post_type)
        
        if location:
            posts = posts.filter(location__icontains=location)
        
        if tags:
            tag_list = [tag.strip() for tag in tags.split(',')]
            for tag in tag_list:
                posts = posts.filter(tags__icontains=tag)
        
        posts = posts.select_related('author').prefetch_related(
            'images', 'author__userprofile'
        ).annotate(
            total_likes=Count('likes', distinct=True),
            total_favorites=Count('favorites', distinct=True),
            comment_count=Count('comments', distinct=True)
        ).order_by('-total_likes', '-created_at')
        
        # Pagination
        paginator = Paginator(posts, 10)
        page_number = request.GET.get('page', 1)
        posts_page = paginator.get_page(page_number)
        
        serializer = PostSerializer(posts_page, many=True, context={'request': request})
        
        return Response({
            'posts': serializer.data,
            'pagination': {
                'current_page': posts_page.number,
                'total_pages': paginator.num_pages,
                'has_next': posts_page.has_next(),
                'has_previous': posts_page.has_previous(),
                'total_posts': paginator.count
            },
            'query': query
        })
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_user_posts(request, user_id=None):
    """
    Get posts by a specific user (or current user if no user_id provided)
    """
    try:
        if user_id:
            user = get_object_or_404(User, id=user_id)
        else:
            user = request.user
        
        # If viewing another user's posts, only show public posts unless following
        if user != request.user:
            is_following = Follow.objects.filter(follower=request.user, following=user).exists()
            if is_following:
                posts = Post.objects.filter(author=user)
            else:
                posts = Post.objects.filter(author=user, is_private=False)
        else:
            # User viewing their own posts - show all
            posts = Post.objects.filter(author=user)
        
        posts = posts.select_related('author').prefetch_related(
            'images', 'author__userprofile'
        ).annotate(
            total_likes=Count('likes', distinct=True),
            total_favorites=Count('favorites', distinct=True),
            comment_count=Count('comments', distinct=True)
        ).order_by('-created_at')
        
        # Pagination
        paginator = Paginator(posts, 10)
        page_number = request.GET.get('page', 1)
        posts_page = paginator.get_page(page_number)
        
        serializer = PostSerializer(posts_page, many=True, context={'request': request})
        user_serializer = UserSerializer(user, context={'request': request})
        
        return Response({
            'user': user_serializer.data,
            'posts': serializer.data,
            'pagination': {
                'current_page': posts_page.number,
                'total_pages': paginator.num_pages,
                'has_next': posts_page.has_next(),
                'has_previous': posts_page.has_previous(),
                'total_posts': paginator.count
            }
        })
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
