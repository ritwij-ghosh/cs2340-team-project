from django.contrib import admin
from django.http import HttpResponse
from django.utils import timezone
import csv
from .models import Application


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('user', 'job_title', 'company_name', 'status', 'applied_on', 'created_at')
    list_filter = ('status', 'applied_on', 'created_at', 'company_name')
    search_fields = ('user__username', 'user__email', 'job_title', 'company_name', 'notes')
    readonly_fields = ('created_at', 'updated_at', 'applied_on')
    date_hierarchy = 'applied_on'
    
    fieldsets = (
        ('Application Details', {
            'fields': ('user', 'job_title', 'company_name', 'status')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('applied_on', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['mark_as_review', 'mark_as_interview', 'mark_as_offer', 'mark_as_closed', 'export_applications_csv']
    
    @admin.action(description='Mark selected applications as Review')
    def mark_as_review(self, request, queryset):
        updated = queryset.update(status=Application.Status.REVIEW)
        self.message_user(request, f"Marked {updated} application(s) as Review.")
    
    @admin.action(description='Mark selected applications as Interview')
    def mark_as_interview(self, request, queryset):
        updated = queryset.update(status=Application.Status.INTERVIEW)
        self.message_user(request, f"Marked {updated} application(s) as Interview.")
    
    @admin.action(description='Mark selected applications as Offer')
    def mark_as_offer(self, request, queryset):
        updated = queryset.update(status=Application.Status.OFFER)
        self.message_user(request, f"Marked {updated} application(s) as Offer.")
    
    @admin.action(description='Mark selected applications as Closed')
    def mark_as_closed(self, request, queryset):
        updated = queryset.update(status=Application.Status.CLOSED)
        self.message_user(request, f"Marked {updated} application(s) as Closed.")
    
    @admin.action(description='Export selected applications to CSV')
    def export_applications_csv(self, request, queryset):
        """Export selected applications to CSV file."""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="applications_export_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'User', 'User Email', 'Job Title', 'Company Name', 'Status', 
            'Applied On', 'Notes', 'Created At', 'Updated At'
        ])
        
        for application in queryset:
            writer.writerow([
                application.user.username,
                application.user.email,
                application.job_title,
                application.company_name,
                application.status,
                application.applied_on.strftime('%Y-%m-%d'),
                application.notes,
                application.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                application.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        return response
