from django.contrib import admin
from django.http import HttpResponse
from django.utils import timezone
import csv
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
    
    actions = ['activate_jobs', 'pause_jobs', 'close_jobs', 'export_jobs_csv']
    
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
    
    @admin.action(description='Export selected jobs to CSV')
    def export_jobs_csv(self, request, queryset):
        """Export selected jobs to CSV file."""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="jobs_export_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Title', 'Company', 'Location', 'Employment Type', 'Experience Level', 
            'Work Type', 'Status', 'Recruiter', 'Salary Min', 'Salary Max', 
            'Visa Sponsorship', 'Application Deadline', 'Created At', 'Updated At'
        ])
        
        for job in queryset:
            writer.writerow([
                job.title,
                job.company,
                job.location,
                job.employment_type,
                job.experience_level,
                job.work_type,
                job.status,
                job.recruiter.username if job.recruiter else 'N/A',
                job.salary_min,
                job.salary_max,
                job.visa_sponsorship,
                job.application_deadline.strftime('%Y-%m-%d') if job.application_deadline else 'N/A',
                job.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                job.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        return response


