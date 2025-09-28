from django.contrib import admin
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
    
    actions = ['mark_as_read', 'mark_as_unread']
    
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
