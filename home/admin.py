from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Task

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_staff', 'created_at')
    fieldsets = UserAdmin.fieldsets + (
        ('プロフィール情報', {'fields': ('profile_image', 'bio', 'affiliation')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('プロフィール情報', {'fields': ('profile_image', 'bio', 'affiliation')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Task)

# Register your models here.
