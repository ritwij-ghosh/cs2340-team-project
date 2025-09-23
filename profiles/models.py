from django.db import models
from django.contrib.auth.models import User
from django.core.validators import URLValidator


class Profile(models.Model):
    """Job seeker profile model with comprehensive information for recruiters."""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    headline = models.CharField(
        max_length=200, 
        help_text="A brief professional headline (e.g., 'Senior Software Engineer')"
    )
    bio = models.TextField(
        max_length=1000, 
        blank=True, 
        help_text="A brief description about yourself and your career goals"
    )
    location = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    
    # Skills
    skills = models.TextField(
        help_text="List your key skills separated by commas (e.g., Python, Django, React, SQL)"
    )
    
    # Education
    education = models.TextField(
        help_text="List your educational background (e.g., 'BS Computer Science - Georgia Tech, 2023')"
    )
    
    # Work Experience
    work_experience = models.TextField(
        help_text="Describe your work experience, including company names, positions, and key achievements"
    )
    
    # Links
    linkedin_url = models.URLField(
        blank=True, 
        validators=[URLValidator()],
        help_text="Your LinkedIn profile URL"
    )
    github_url = models.URLField(
        blank=True, 
        validators=[URLValidator()],
        help_text="Your GitHub profile URL"
    )
    portfolio_url = models.URLField(
        blank=True, 
        validators=[URLValidator()],
        help_text="Your portfolio or personal website URL"
    )
    other_url = models.URLField(
        blank=True, 
        validators=[URLValidator()],
        help_text="Any other relevant URL (e.g., personal blog, Stack Overflow)"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}'s Profile"
    
    def get_skills_list(self):
        """Return skills as a list for easier template rendering."""
        return [skill.strip() for skill in self.skills.split(',') if skill.strip()]
    
    def has_links(self):
        """Check if profile has any social/professional links."""
        return any([self.linkedin_url, self.github_url, self.portfolio_url, self.other_url])
