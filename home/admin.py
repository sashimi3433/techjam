from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Task, Friendship, FriendRequest ,TimelineActivity

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_staff', 'created_at', 'experience_points', 'tasks_completed')
    fieldsets = UserAdmin.fieldsets + (
        ('プロフィール情報', {'fields': ('profile_image', 'bio', 'affiliation')}),
        ('進捗情報', {'fields': ('experience_points', 'tasks_completed')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('プロフィール情報', {'fields': ('profile_image', 'bio', 'affiliation')}),
        ('進捗情報', {'fields': ('experience_points', 'tasks_completed')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Task)
admin.site.register(Friendship)
admin.site.register(FriendRequest)
admin.site.register(TimelineActivity)

# Register your models here.
