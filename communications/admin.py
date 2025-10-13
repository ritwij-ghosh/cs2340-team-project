from django.contrib import admin
from django.http import HttpResponse
from django.utils import timezone
import csv
from .models import Message


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'sender', 'recipient', 'sent_at', 'is_read')
    list_filter = ('sent_at', 'read_at', 'sender', 'recipient')
    search_fields = ('subject', 'body', 'sender__username', 'recipient__username')
    readonly_fields = ('sent_at', 'read_at')
    date_hierarchy = 'sent_at'
    
    fieldsets = (
        ('Message Details', {
            'fields': ('sender', 'recipient', 'subject', 'body')
        }),
        ('Timestamps', {
            'fields': ('sent_at', 'read_at'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['mark_as_read', 'mark_as_unread', 'export_messages_csv']
    
    @admin.action(description='Mark selected messages as read')
    def mark_as_read(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(read_at=timezone.now())
        self.message_user(request, f"Marked {updated} message(s) as read.")
    
    @admin.action(description='Mark selected messages as unread')
    def mark_as_unread(self, request, queryset):
        updated = queryset.update(read_at=None)
        self.message_user(request, f"Marked {updated} message(s) as unread.")
    
    def is_read(self, obj):
        return obj.is_read()
    is_read.boolean = True
    is_read.short_description = 'Read'
    
    @admin.action(description='Export selected messages to CSV')
    def export_messages_csv(self, request, queryset):
        """Export selected messages to CSV file."""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="messages_export_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Subject', 'Sender', 'Sender Email', 'Recipient', 'Recipient Email', 
            'Body', 'Sent At', 'Read At', 'Is Read'
        ])
        
        for message in queryset:
            writer.writerow([
                message.subject,
                message.sender.username,
                message.sender.email,
                message.recipient.username,
                message.recipient.email,
                message.body,
                message.sent_at.strftime('%Y-%m-%d %H:%M:%S'),
                message.read_at.strftime('%Y-%m-%d %H:%M:%S') if message.read_at else 'Not Read',
                'Yes' if message.is_read() else 'No'
            ])
        
        return response
