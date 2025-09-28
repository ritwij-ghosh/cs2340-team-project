from django.contrib import admin
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'headline', 'location', 'is_public', 'created_at')
    list_filter = ('is_public', 'show_bio', 'show_location', 'show_education', 'created_at')
    search_fields = ('user__username', 'user__email', 'headline', 'location', 'skills')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'headline', 'bio', 'location')
        }),
        ('Professional Details', {
            'fields': ('skills', 'education', 'work_experience')
        }),
        ('Links', {
            'fields': ('linkedin_url', 'github_url', 'portfolio_url', 'other_url'),
            'classes': ('collapse',)
        }),
        ('Privacy Settings', {
            'fields': ('is_public', 'show_bio', 'show_location', 'show_phone', 
                      'show_education', 'show_work_experience', 'show_links'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
