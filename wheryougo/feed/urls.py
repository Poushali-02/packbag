from django.urls import path
from . import views

urlpatterns = [
    path('', views.feed, name='feed'),
    path('create_post/', views.create_post, name='create_post'),
    path('ajax/upload-image/', views.ajax_upload_image, name='ajax_upload_image'),
    path('ajax/tag-suggestions/', views.get_tag_suggestions, name='tag_suggestions'),
    path('post/<int:post_id>/like/', views.toggle_like, name='toggle_like'),
    path('post/<int:post_id>/favourite/', views.toggle_favourite, name='toggle_favourite'),
    path('comment/<int:comment_id>/like_comment/', views.toggle_comment_like, name='toggle_comment_like'),
    path('view_post/<int:post_id>/', views.view_post, name='view_post'),
    path('comment/<int:post_id>/', views.comment, name='comment'),
]
