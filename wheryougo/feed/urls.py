from django.urls import path
from . import views

urlpatterns = [
    # API endpoints for frontend
    path('api/feed/', views.api_feed, name='api_feed'),
    path('api/posts/create/', views.api_create_post, name='api_create_post'),
    path('api/posts/<int:post_id>/', views.api_get_post, name='api_get_post'),
    path('api/posts/<int:post_id>/like/', views.api_toggle_like, name='api_toggle_like'),
    path('api/posts/<int:post_id>/favorite/', views.api_toggle_favorite, name='api_toggle_favorite'),
    path('api/posts/<int:post_id>/comment/', views.api_add_comment, name='api_add_comment'),
    path('api/comments/<int:comment_id>/like/', views.api_toggle_comment_like, name='api_toggle_comment_like'),
    path('api/tags/suggestions/', views.api_get_tag_suggestions, name='api_tag_suggestions'),
    path('api/posts/search/', views.api_search_posts, name='api_search_posts'),
    path('api/users/<int:user_id>/posts/', views.api_user_posts, name='api_user_posts'),
    path('api/users/posts/', views.api_user_posts, name='api_current_user_posts'),  # Current user's posts
]
