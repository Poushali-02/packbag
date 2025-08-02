from django.shortcuts import render
from .models import Notification

# Create your views here.

def notification_list(request):
    notifications = Notification.objects.filter(to_user=request.user).select_related('from_user', 'post', 'comment').order_by('-created_at')[:5]

    all_notifications = Notification.objects.filter(to_user=request.user)
    return render(request, 'feed/_notification_list.html', {'notifications': notifications, 'total_notifications': all_notifications.count()})

def notification_list_all(request):
    notifications = Notification.objects.filter(to_user=request.user).select_related('from_user', 'post', 'comment').order_by('-created_at')

    return render(request, 'feed/all_notification_list.html', {'notifications': notifications, 'total_notifications': notifications.count()})