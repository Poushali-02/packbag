from django.urls import path
from . import views

urlpatterns = [
    path('', views.trips, name='trips'),
    path('user/<str:username>/', views.trips_user, name='trips_user'),
    path('view/<int:trip_id>/', views.trip_detail, name='trip_detail'),
]