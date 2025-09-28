from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    """Extended user profile to store user type and additional information."""
    
    USER_TYPE_CHOICES = [
        ('job_seeker', 'Job Seeker'),
        ('recruiter', 'Recruiter'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_profile')
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        help_text="Type of user: job seeker or recruiter"
    )
    company = models.CharField(
        max_length=200,
        blank=True,
        help_text="Company name (for recruiters)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} ({self.get_user_type_display()})"
    
    def is_job_seeker(self):
        """Check if user is a job seeker."""
        return self.user_type == 'job_seeker'
    
    def is_recruiter(self):
        """Check if user is a recruiter."""
        return self.user_type == 'recruiter'
