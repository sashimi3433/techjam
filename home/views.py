from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CustomUser, Task, TimelineActivity, FriendRequest, Friendship
from django.utils import timezone
from datetime import timedelta

def index(request):
    if request.user.is_authenticated:
        # Delete tasks older than 24 hours
        expiry_time = timezone.now() - timedelta(hours=24)
        Task.objects.filter(created_at__lte=expiry_time).delete()
        
        # Get remaining tasks
        tasks = Task.objects.filter(user=request.user)
        completed_tasks_count = tasks.filter(status='completed').count()
        in_progress_tasks_count = tasks.filter(status='in_progress').count()
        not_started_tasks_count = tasks.filter(status='not_started').count()
        context = {
            'tasks': tasks,
            'completed_tasks_count': completed_tasks_count,
            'in_progress_tasks_count': in_progress_tasks_count,
            'not_started_tasks_count': not_started_tasks_count,
        }
        return render(request, 'home/index.html', context)
    else:
        return render(request, 'home/landing.html')

@login_required
def add(request):
    if request.method == 'POST':
        try:
            task = Task(
                title=request.POST['title'],
                description=request.POST['description'],
                user=request.user
            )
            task.save()
            
            # タスク作成のアクティビティを記録
            TimelineActivity.objects.create(
                user=request.user,
                activity_type='task_created',
                content=f'新しいタスク「{task.title}」を作成しました',
                related_task=task
            )
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
    task = get_object_or_404(Task, id=task_id, user=request.user)
    task.status = 'completed'
    task.save()
    
    # タスク完了のアクティビティを記録
    TimelineActivity.objects.create(
        user=request.user,
        activity_type='task_completed',
        content=f'タスク「{task.title}」を完了しました',
        related_task=task
    )
    return redirect('progress')

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
    completed_tasks_count = tasks.filter(status='completed').count()
    ongoing_tasks_count = tasks.filter(status='ongoing').count()
    
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
    completed_tasks_count = tasks.filter(status='completed').count()
    in_progress_tasks_count = tasks.filter(status='in_progress').count()
    not_started_tasks_count = tasks.filter(status='not_started').count()
    total_tasks_count = tasks.count()
    
    context = {
        'user': user,
        'completed_tasks_count': completed_tasks_count,
        'in_progress_tasks_count': in_progress_tasks_count,
        'not_started_tasks_count': not_started_tasks_count,
        'total_tasks_count': total_tasks_count,
        'tasks': tasks
    }
    
    return render(request, 'home/progress.html', context)

@login_required
def timeline_view(request):
    from .models import TimelineActivity
    
    # Get all activities for the current user and their friends
    activities = TimelineActivity.objects.select_related('user', 'related_task').order_by('-created_at')
    
    context = {
        'user': request.user,
        'activities': activities
    }
    
    return render(request, 'home/timeline.html', context)

@login_required
def friends_view(request):
    search_query = request.GET.get('search', '')
    search_results = None

    if search_query:
        search_results = CustomUser.objects.filter(username__icontains=search_query).exclude(id=request.user.id)

    # Get pending friend requests
    pending_requests = FriendRequest.objects.filter(receiver=request.user, status='pending')
    # Get user's friends through Friendship model
    friendships = Friendship.objects.filter(user=request.user)
    friends = [friendship.friend for friendship in friendships]

    context = {
        'search_query': search_query,
        'search_results': search_results,
        'pending_requests': pending_requests,
        'friends': friends,
    }
    return render(request, 'home/friends.html', context)

@login_required
def send_friend_request(request, user_id):
    if request.method == 'POST':
        receiver = get_object_or_404(CustomUser, id=user_id)
        # Check if there's an active friendship
        if not Friendship.objects.filter(user=request.user, friend=receiver).exists():
            # Check if there's a pending request
            existing_request = FriendRequest.objects.filter(sender=request.user, receiver=receiver).first()
            if existing_request:
                if existing_request.status in ['rejected']:
                    # If previous request was rejected, create a new one
                    existing_request.delete()
                    FriendRequest.objects.create(sender=request.user, receiver=receiver)
            else:
                # Create new friend request if none exists
                FriendRequest.objects.create(sender=request.user, receiver=receiver)
    return redirect('friends')

@login_required
def remove_friend(request, friend_id):
    if request.method == 'POST':
        friend = get_object_or_404(CustomUser, id=friend_id)
        # Delete bidirectional friendship
        Friendship.objects.filter(user=request.user, friend=friend).delete()
        Friendship.objects.filter(user=friend, friend=request.user).delete()
    return redirect('friends')

@login_required
def accept_friend_request(request, request_id):
    if request.method == 'POST':
        friend_request = get_object_or_404(FriendRequest, id=request_id, receiver=request.user)
        friend_request.status = 'accepted'
        friend_request.save()
        # Create bidirectional friendship
        Friendship.objects.create(user=request.user, friend=friend_request.sender)
        Friendship.objects.create(user=friend_request.sender, friend=request.user)
    return redirect('friends')

@login_required
def remove_friend(request, friend_id):
    if request.method == 'POST':
        friend = get_object_or_404(CustomUser, id=friend_id)
        # Delete bidirectional friendship
        Friendship.objects.filter(user=request.user, friend=friend).delete()
        Friendship.objects.filter(user=friend, friend=request.user).delete()
    return redirect('friends')

@login_required
def reject_friend_request(request, request_id):
    if request.method == 'POST':
        friend_request = get_object_or_404(FriendRequest, id=request_id, receiver=request.user)
        friend_request.status = 'rejected'
        friend_request.save()
    return redirect('friends')