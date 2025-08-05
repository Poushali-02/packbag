from django.shortcuts import render, redirect
from .models import Trip
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.contrib import messages
from .models import Trip
from django.db.models import Q
from manage.models import UserProfile

@login_required
def trips(request):
    all_trips = Trip.objects.all()
    return render(request, 'trip/trips.html', {'trips': all_trips})

@login_required
def trip_detail(request, trip_id):
    trip = get_object_or_404(Trip, id=trip_id)
    context = {
        'trip': trip,
    }
    return render(request, 'trip/trip_detail.html', context)

@login_required
def trips_user(request, username):
    if username:
        # Viewing someone else's profile
        profile_user = get_object_or_404(User, username=username)
    else:
        # Viewing own profile (if logged in)
        if not request.user.is_authenticated:
            return redirect('signin')
        profile_user = request.user
    
    # Get or create user profile
    try:
        user_profile = UserProfile.objects.get(user=profile_user)
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(
            user=profile_user,
            name=profile_user.first_name or profile_user.username,
            user_type='traveler'
        )
    
    
    # Get trips data
    created_trips = Trip.objects.filter(created_by=profile_user).order_by('-created_at')
    participated_trips = Trip.objects.filter(members=profile_user).exclude(created_by=profile_user).order_by('-created_at')
    
    # Combine and get counts
    all_user_trips = Trip.objects.filter(
        Q(created_by=profile_user) | Q(members=profile_user)
    ).distinct().order_by('-created_at')
    
    trips_count = all_user_trips.count()
    created_trips_count = created_trips.count()
    participated_trips_count = participated_trips.count()

    context = {
        'created_trips': created_trips,
        'participated_trips': participated_trips,
        'all_user_trips': all_user_trips,
        'trips_count': trips_count,
        'created_trips_count': created_trips_count,
        'participated_trips_count': participated_trips_count
    }
    return render(request, 'trip/_each_trip.html', context)