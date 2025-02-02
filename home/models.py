from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

class FriendRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', '保留中'),
        ('accepted', '承認済み'),
        ('rejected', '拒否')
    ]

    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_friend_requests')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_friend_requests')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('sender', 'receiver')

class Friendship(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='friendships')
    friend = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='friends')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'friend')

class Task(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']

class TimelineActivity(models.Model):
    ACTIVITY_TYPES = [
        ('task_created', 'タスク開始'),
        ('task_completed', 'タスク完了')
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    content = models.TextField()
    related_task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

class CustomUser(AbstractUser):
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    affiliation = models.CharField(max_length=100, blank=True)
    experience_points = models.IntegerField(default=0)
    tasks_completed = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    # 更新日時
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def level(self):
        # Level up every 100 experience points
        return (self.experience_points // 100) + 1

    @property
    def task_rank(self):
        # Rank up every 5 completed tasks
        return (self.tasks_completed // 5) + 1

    @property
    def next_level_progress(self):
        # Calculate progress to next level (0-100)
        current_level_xp = (self.level - 1) * 100
        next_level_xp = self.level * 100
        return ((self.experience_points - current_level_xp) / (next_level_xp - current_level_xp)) * 100

    @property
    def completed_tasks_count(self):
        return self.tasks_completed

    class Meta:
        verbose_name = 'ユーザー'
        verbose_name_plural = 'ユーザー'

    def __str__(self):
        return self.username

class TimelineActivity(models.Model):
    ACTIVITY_TYPES = [
        ('task_created', 'タスク作成'),
        ('task_completed', 'タスク完了'),
        ('level_up', 'レベルアップ'),
        ('friend_added', '友達追加')
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=50, choices=ACTIVITY_TYPES)
    content = models.TextField()
    related_task = models.ForeignKey(Task, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'タイムラインアクティビティ'
        verbose_name_plural = 'タイムラインアクティビティ'

    def __str__(self):
        return f'{self.user.username} - {self.get_activity_type_display()} - {self.created_at}'
