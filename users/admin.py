from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Profile

# Register your custom user model and the related profile model
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'is_superuser')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_active', 'is_staff')
        }),
    )
    search_fields = ('username', 'email')
    ordering = ('username',)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'farm_name', 'phone', 'location')
    search_fields = ('user__username', 'farm_name', 'location')
    list_filter = ('farm_name',)
