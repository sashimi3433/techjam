from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .models import CustomUser, Task

from django.utils import timezone
from datetime import timedelta

def index(request):
    if request.user.is_authenticated:
        # Delete tasks older than 24 hours
        expiry_time = timezone.now() - timedelta(hours=24)
        Task.objects.filter(created_at__lte=expiry_time).delete()
        
        # Get remaining tasks
        tasks = Task.objects.filter(user=request.user)
    else:
        tasks = []
    return render(request, 'home/index.html', {'tasks': tasks})

def add(request):
    if request.method == 'POST':
        try:
            task = Task(
                title=request.POST['title'],
                description=request.POST['description'],
                priority=request.POST['priority'],
                user=request.user
            )
            task.save()
            return redirect('index')
        except Exception as e:
            return render(request, 'home/add.html', {'error': str(e)})
    return render(request, 'home/add.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            return render(request, 'home/login.html', {'error': 'ユーザー名またはパスワードが間違っています。'})
    return render(request, 'home/login.html')

def register_view(request):
    if request.method == 'POST':
        if request.POST['password1'] != request.POST['password2']:
            return render(request, 'home/register.html', {'error': 'パスワードが一致しません。'})
        try:
            user = CustomUser.objects.create_user(
                username=request.POST['username'],
                email=request.POST['email'],
                password=request.POST['password1'],
                bio=request.POST.get('bio', ''),
                affiliation=request.POST.get('affiliation', '')
            )
            if 'profile_image' in request.FILES:
                user.profile_image = request.FILES['profile_image']
                user.save()
            login(request, user)
            return redirect('index')
        except Exception as e:
            return render(request, 'home/register.html', {'error': 'ユーザー登録に失敗しました。'})
    return render(request, 'home/register.html')

def logout_view(request):
    logout(request)
    return redirect('login')