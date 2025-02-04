from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('add/', views.add, name='add'),
    path('accounts/login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('mypage/', views.mypage_view, name='mypage'),
    path('progress/', views.progress_view, name='progress'),
    path('update-task-status/<int:task_id>/', views.update_task_status, name='update_task_status'),
    path('timeline/', views.timeline_view, name='timeline'),
    path('friends/', views.friends_view, name='friends'),
    path('send-friend-request/<int:user_id>/', views.send_friend_request, name='send_friend_request'),
    path('accept-friend-request/<int:request_id>/', views.accept_friend_request, name='accept_friend_request'),
    path('reject-friend-request/<int:request_id>/', views.reject_friend_request, name='reject_friend_request'),
    path('remove-friend/<int:friend_id>/', views.remove_friend, name='remove_friend'),
    path('duplicate-task/<int:task_id>/', views.duplicate_task, name='duplicate_task'),
]
