from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.utils import timezone
import csv
from .models import UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'


class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_user_type', 'get_company')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'user_profile__company')
    actions = ['export_users_csv']

    def get_user_type(self, obj):
        try:
            return obj.user_profile.user_type
        except UserProfile.DoesNotExist:
            return 'No Profile'
    get_user_type.short_description = 'User Type'

    def get_company(self, obj):
        try:
            return obj.user_profile.company
        except UserProfile.DoesNotExist:
            return 'N/A'
    get_company.short_description = 'Company'
    
    @admin.action(description='Export selected users to CSV')
    def export_users_csv(self, request, queryset):
        """Export selected users to CSV file."""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="users_export_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Username', 'Email', 'First Name', 'Last Name', 'User Type', 
            'Company', 'Is Staff', 'Is Active', 'Date Joined', 'Last Login'
        ])
        
        for user in queryset:
            try:
                user_type = user.user_profile.user_type
                company = user.user_profile.company
            except UserProfile.DoesNotExist:
                user_type = 'No Profile'
                company = 'N/A'
            
            writer.writerow([
                user.username,
                user.email,
                user.first_name,
                user.last_name,
                user_type,
                company,
                user.is_staff,
                user.is_active,
                user.date_joined.strftime('%Y-%m-%d %H:%M:%S'),
                user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else 'Never'
            ])
        
        return response


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_type', 'company', 'created_at')
    list_filter = ('user_type', 'company', 'created_at')
    search_fields = ('user__username', 'user__email', 'company')
    readonly_fields = ('created_at',)
    actions = ['export_user_profiles_csv']
    
    @admin.action(description='Export selected user profiles to CSV')
    def export_user_profiles_csv(self, request, queryset):
        """Export selected user profiles to CSV file."""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="user_profiles_export_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'User', 'User Email', 'User Type', 'Company', 'Created At'
        ])
        
        for user_profile in queryset:
            writer.writerow([
                user_profile.user.username,
                user_profile.user.email,
                user_profile.user_type,
                user_profile.company,
                user_profile.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        return response


# Unregister the default User admin and register our custom one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
