from django.contrib import admin
from django.http import HttpResponse
from django.utils import timezone
import csv
from .models import Profile, SavedCandidateSearch


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'headline', 'location', 'is_public', 'created_at')
    list_filter = ('is_public', 'show_bio', 'show_location', 'show_education', 'created_at')
    search_fields = ('user__username', 'user__email', 'headline', 'location', 'skills')
    readonly_fields = ('created_at', 'updated_at')
    actions = ['export_profiles_csv']
    
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
    
    @admin.action(description='Export selected profiles to CSV')
    def export_profiles_csv(self, request, queryset):
        """Export selected profiles to CSV file."""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="profiles_export_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'User', 'User Email', 'Headline', 'Bio', 'Location', 'Skills', 
            'Education', 'Work Experience', 'LinkedIn URL', 'GitHub URL', 
            'Portfolio URL', 'Other URL', 'Is Public', 'Show Bio', 'Show Location', 
            'Show Phone', 'Show Education', 'Show Work Experience', 'Show Links', 
            'Created At', 'Updated At'
        ])
        
        for profile in queryset:
            writer.writerow([
                profile.user.username,
                profile.user.email,
                profile.headline,
                profile.bio,
                profile.location,
                profile.skills,
                profile.education,
                profile.work_experience,
                profile.linkedin_url,
                profile.github_url,
                profile.portfolio_url,
                profile.other_url,
                profile.is_public,
                profile.show_bio,
                profile.show_location,
                profile.show_phone,
                profile.show_education,
                profile.show_work_experience,
                profile.show_links,
                profile.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                profile.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        return response


@admin.register(SavedCandidateSearch)
class SavedCandidateSearchAdmin(admin.ModelAdmin):
    list_display = ('user', 'skills', 'location', 'projects', 'created_at', 'last_checked_at', 'last_notified_count')
    list_filter = ('created_at', 'last_checked_at')
    search_fields = ('user__username', 'skills', 'location', 'projects')
