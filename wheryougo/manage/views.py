from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from .models import UserProfile
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import logout

@csrf_protect
def signup(request):
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            dob = request.POST.get('dob')
            
            # Check if username already exists
            if User.objects.filter(username=username).exists():
                return render(request, 'website/signup.html', {
                    'error': f'Username "{username}" is already taken. Please choose a different username.'
                })
            
            # Check if email already exists
            if User.objects.filter(email=email).exists():
                return render(request, 'website/signup.html', {
                    'error': f'An account with email "{email}" already exists. Please use a different email or sign in.'
                })
            
            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            
            # Create profile
            profile = UserProfile.objects.create(
                user=user,
                name=name,
                date_of_birth=dob  # Fix field name to match your model
            )
            
            login(request, user)
            return redirect('feed')  # Redirect to feed instead of rendering signup
            
        except Exception as e:
            return render(request, 'website/signup.html', {'error': str(e)})
    
    return render(request, 'website/signup.html')

@csrf_protect
def signin(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('feed')
            else:
                return render(request, 'website/signin.html', {'error': 'Invalid credentials'})
    return render(request, 'website/signin.html')
  
def logout_user(request):
    logout(request)
    return redirect('home')