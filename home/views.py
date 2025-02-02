from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
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
        context = {
            'tasks': tasks,
            'user': request.user
        }
    else:
        context = {
            'tasks': [],
            'user': None
        }
    return render(request, 'home/index.html', context)

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
            return render(request, 'home/add.html', {'error': str(e), 'user': request.user})
    return render(request, 'home/add.html', {'user': request.user})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            return render(request, 'home/login.html', {'error': 'ユーザー名またはパスワードが間違っています。', 'user': None})
    return render(request, 'home/login.html', {'user': None})

def register_view(request):
    if request.method == 'POST':
        if request.POST['password1'] != request.POST['password2']:
            return render(request, 'home/register.html', {'error': 'パスワードが一致しません。', 'user': None})
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
            return render(request, 'home/register.html', {'error': 'ユーザー登録に失敗しました。', 'user': None})
    return render(request, 'home/register.html', {'user': None})

@login_required
def complete_task(request, task_id):
    if request.method == 'POST':
        task = Task.objects.get(id=task_id, user=request.user)
        task.completed = True
        task.save()
        return redirect('index')
    return redirect('index')

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

@login_required
def mypage_view(request):
    user = request.user
    tasks = Task.objects.filter(user=user)
    completed_tasks_count = tasks.filter(completed=True).count()
    ongoing_tasks_count = tasks.filter(completed=False).count()
    
    if request.method == 'POST':
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        if 'profile_image' in request.FILES:
            user.profile_image = request.FILES['profile_image']
        user.save()
        return redirect('mypage')
    
    context = {
        'user': user,
        'completed_tasks_count': completed_tasks_count,
        'ongoing_tasks_count': ongoing_tasks_count
    }
    return render(request, 'home/mypage.html', context)

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def progress_view(request):
    user = request.user
    tasks = Task.objects.filter(user=user)
    
    # Calculate task statistics
    completed_tasks_count = tasks.filter(completed=True).count()
    ongoing_tasks_count = tasks.filter(completed=False).count()
    total_tasks_count = tasks.count()
    
    # Get tasks by priority
    high_priority_tasks = tasks.filter(priority='high')
    medium_priority_tasks = tasks.filter(priority='medium')
    low_priority_tasks = tasks.filter(priority='low')
    
    context = {
        'user': user,
        'completed_tasks_count': completed_tasks_count,
        'ongoing_tasks_count': ongoing_tasks_count,
        'total_tasks_count': total_tasks_count,
        'high_priority_tasks': high_priority_tasks,
        'medium_priority_tasks': medium_priority_tasks,
        'low_priority_tasks': low_priority_tasks
    }
    
    return render(request, 'home/progress.html', context)