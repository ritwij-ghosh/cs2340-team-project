from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'


class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_user_type', 'get_company')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'userprofile__company')

    def get_user_type(self, obj):
        try:
            return obj.userprofile.user_type
        except UserProfile.DoesNotExist:
            return 'No Profile'
    get_user_type.short_description = 'User Type'

    def get_company(self, obj):
        try:
            return obj.userprofile.company
        except UserProfile.DoesNotExist:
            return 'N/A'
    get_company.short_description = 'Company'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_type', 'company', 'created_at')
    list_filter = ('user_type', 'company', 'created_at')
    search_fields = ('user__username', 'user__email', 'company')
    readonly_fields = ('created_at',)


# Unregister the default User admin and register our custom one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
