from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CustomUser, Task, FriendRequest, Friendship
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
        'completed_tasks_count': completed_tasks_count,
        'ongoing_tasks_count': ongoing_tasks_count,
        'total_tasks_count': total_tasks_count,
        'high_priority_tasks': high_priority_tasks,
        'medium_priority_tasks': medium_priority_tasks,
        'low_priority_tasks': low_priority_tasks
    }
    
    return render(request, 'home/progress.html', context)

@login_required
def friends(request):
    user = request.user
    friends = user.get_friends()
    pending_requests = user.get_pending_friend_requests()
    
    context = {
        'friends': friends,
        'pending_requests': pending_requests
    }
    return render(request, 'home/friends.html', context)

@login_required
def send_friend_request(request, user_id):
    if request.method == 'POST':
        receiver = get_object_or_404(CustomUser, id=user_id)
        if receiver != request.user:
            FriendRequest.objects.get_or_create(sender=request.user, receiver=receiver)
    return redirect('friends')

@login_required
def accept_friend_request(request, request_id):
    if request.method == 'POST':
        friend_request = get_object_or_404(FriendRequest, id=request_id, receiver=request.user, status='pending')
        friend_request.status = 'accepted'
        friend_request.save()
        
        # Create friendship
        Friendship.objects.create(user=request.user, friend=friend_request.sender)
        Friendship.objects.create(user=friend_request.sender, friend=request.user)
    return redirect('friends')

@login_required
def reject_friend_request(request, request_id):
    if request.method == 'POST':
        friend_request = get_object_or_404(FriendRequest, id=request_id, receiver=request.user, status='pending')
        friend_request.status = 'rejected'
        friend_request.save()
    return redirect('friends')

@login_required
def remove_friend(request, friend_id):
    if request.method == 'POST':
        friend = get_object_or_404(CustomUser, id=friend_id)
        Friendship.objects.filter(user=request.user, friend=friend).delete()
        Friendship.objects.filter(user=friend, friend=request.user).delete()
    return redirect('friends')