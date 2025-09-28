from django.contrib import admin
from .models import Job


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'location', 'employment_type', 'work_type', 'status', 'recruiter', 'created_at')
    list_filter = ('status', 'employment_type', 'work_type', 'experience_level', 'company', 'location', 'created_at')
    search_fields = ('title', 'company', 'location', 'description', 'requirements', 'recruiter__username')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'company', 'location', 'recruiter')
        }),
        ('Job Details', {
            'fields': ('employment_type', 'experience_level', 'work_type', 'status')
        }),
        ('Requirements & Skills', {
            'fields': ('description', 'requirements', 'skills_required')
        }),
        ('Compensation & Benefits', {
            'fields': ('salary_min', 'salary_max', 'benefits'),
            'classes': ('collapse',)
        }),
        ('Additional Settings', {
            'fields': ('visa_sponsorship', 'application_deadline', 'external_url'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['activate_jobs', 'pause_jobs', 'close_jobs']
    
    @admin.action(description='Activate selected jobs')
    def activate_jobs(self, request, queryset):
        updated = queryset.update(status='active')
        self.message_user(request, f"Activated {updated} job(s).")
    
    @admin.action(description='Pause selected jobs')
    def pause_jobs(self, request, queryset):
        updated = queryset.update(status='paused')
        self.message_user(request, f"Paused {updated} job(s).")
    
    @admin.action(description='Close selected jobs')
    def close_jobs(self, request, queryset):
        updated = queryset.update(status='closed')
        self.message_user(request, f"Closed {updated} job(s).")


