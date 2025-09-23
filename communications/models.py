from django.db import models
from django.contrib.auth.models import User
from profiles.models import Profile


class EmailMessage(models.Model):
    """Email message model for recruiter-candidate communication."""
    
    # Sender and recipient
    sender = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='sent_emails',
        help_text="The recruiter sending the email"
    )
    recipient = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='received_emails',
        help_text="The candidate receiving the email"
    )
    
    # Email content
    subject = models.CharField(
        max_length=200,
        help_text="Email subject line"
    )
    message = models.TextField(
        help_text="Email message content"
    )
    
    # Email metadata
    sent_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    is_read = models.BooleanField(default=False)
    
    # Email type and status
    EMAIL_TYPES = [
        ('job_opportunity', 'Job Opportunity'),
        ('interview_request', 'Interview Request'),
        ('follow_up', 'Follow Up'),
        ('general', 'General Inquiry'),
        ('rejection', 'Rejection'),
    ]
    
    email_type = models.CharField(
        max_length=20,
        choices=EMAIL_TYPES,
        default='general',
        help_text="Type of email being sent"
    )
    
    # Optional job reference
    job_title = models.CharField(
        max_length=200,
        blank=True,
        help_text="Job title if this email is related to a specific position"
    )
    company_name = models.CharField(
        max_length=200,
        blank=True,
        help_text="Company name if this email is from a specific company"
    )
    
    class Meta:
        ordering = ['-sent_at']
        verbose_name = 'Email Message'
        verbose_name_plural = 'Email Messages'
    
    def __str__(self):
        return f"{self.subject} - {self.sender.username} to {self.recipient.username}"
    
    def mark_as_read(self):
        """Mark the email as read."""
        if not self.is_read:
            from django.utils import timezone
            self.is_read = True
            self.read_at = timezone.now()
            self.save()
    
    def get_recipient_profile(self):
        """Get the recipient's profile if it exists."""
        try:
            return self.recipient.profile
        except Profile.DoesNotExist:
            return None
    
    def get_sender_profile(self):
        """Get the sender's profile if it exists."""
        try:
            return self.sender.profile
        except Profile.DoesNotExist:
            return None
