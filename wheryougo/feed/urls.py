from django.urls import path
from . import views

urlpatterns = [
    path('', views.feed, name='feed'),
    path('create_post/', views.create_post, name='create_post'),
    path('ajax/upload-image/', views.ajax_upload_image, name='ajax_upload_image'),
    path('ajax/tag-suggestions/', views.get_tag_suggestions, name='tag_suggestions'),

]
