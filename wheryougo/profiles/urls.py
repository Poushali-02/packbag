from django.urls import path
from . import views

urlpatterns = [
    path('', views.profile, name='profile'),
    path('<str:username>/', views.profile, name='profile'),       # /profile/username/ → any user's profile
    path('edit/<str:username>/', views.edit_profile, name='edit_profile'),
    path('ajax/follow/<str:username>/', views.follow_user, name='follow_user'),
]