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
    path('complete-task/<int:task_id>/', views.complete_task, name='complete_task'),
    path('timeline/', views.timeline_view, name='timeline'),
]
