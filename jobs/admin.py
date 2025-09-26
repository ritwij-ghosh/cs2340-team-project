from django.contrib import admin
from .models import Job


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'location', 'status', 'created_at')
    list_filter = ('status', 'company', 'location', 'created_at')
    search_fields = ('title', 'company', 'location', 'description')
    actions = ['approve_jobs', 'reject_jobs']

    @admin.action(description='Approve selected jobs')
    def approve_jobs(self, request, queryset):
        updated = queryset.update(status=Job.ModerationStatus.APPROVED)
        self.message_user(request, f"Approved {updated} job(s).")

    @admin.action(description='Reject selected jobs')
    def reject_jobs(self, request, queryset):
        updated = queryset.update(status=Job.ModerationStatus.REJECTED)
        self.message_user(request, f"Rejected {updated} job(s).")


