from django.db import models
from django.contrib.auth.models import User
from django.core.validators import EmailValidator


class Message(models.Model):
    """Message model for recruiter-candidate communication."""
    
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        help_text="User who sent the message"
    )
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_messages',
        help_text="User who received the message"
    )
    subject = models.CharField(
        max_length=200,
        help_text="Message subject line"
    )
    body = models.TextField(
        help_text="Message content"
    )
    sent_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-sent_at']
    
    def __str__(self):
        return f"From {self.sender.username} to {self.recipient.username}: {self.subject}"
    
    def mark_as_read(self):
        """Mark message as read."""
        if not self.read_at:
            from django.utils import timezone
            self.read_at = timezone.now()
            self.save(update_fields=['read_at'])
    
    def is_read(self):
        """Check if message has been read."""
        return self.read_at is not None
