from django.urls import path
from . import views

urlpatterns = [
    path('show/', views.notification_list, name='notification_list'),
    path('show/all/', views.notification_list_all, name='notification_list_all'),
]