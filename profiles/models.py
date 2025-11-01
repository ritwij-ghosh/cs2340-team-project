from django.db import models
from django.contrib.auth.models import User
from django.core.validators import URLValidator, RegexValidator


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
    phone = models.CharField(
        max_length=20,
        blank=True,
        validators=[RegexValidator(r'^\d{10}$', 'Enter a valid 10-digit US phone number.')]
    )
    
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
    
    # Resume
    resume = models.FileField(
        upload_to='resumes/',
        blank=True,
        null=True,
        help_text="Upload your resume (PDF, DOC, or DOCX format)"
    )
    
    # Commute Preferences
    commute_radius = models.PositiveIntegerField(
        default=50,
        help_text="Preferred commute radius in miles (default: 50 miles)"
    )

    # Privacy Settings
    is_public = models.BooleanField(
        default=True,
        help_text="Allow recruiters to find and view your profile."
    )
    show_bio = models.BooleanField(
        default=True,
        help_text="Display your bio on your public profile."
    )
    show_location = models.BooleanField(
        default=True,
        help_text="Display your location on your public profile."
    )
    show_phone = models.BooleanField(
        default=False,
        help_text="Display your phone number so recruiters can contact you directly."
    )
    show_education = models.BooleanField(
        default=True,
        help_text="Display your education history on your public profile."
    )
    show_work_experience = models.BooleanField(
        default=True,
        help_text="Display your work experience on your public profile."
    )
    show_links = models.BooleanField(
        default=True,
        help_text="Display your professional links to recruiters."
    )
    show_resume = models.BooleanField(
        default=True,
        help_text="Allow recruiters to download your resume."
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

    def has_public_links(self):
        """Check if links should be shown to other users."""
        return self.show_links and self.has_links()
    
    def has_resume(self):
        """Check if profile has a resume uploaded."""
        return bool(self.resume)
    
    def has_public_resume(self):
        """Check if resume should be shown to other users."""
        return self.show_resume and self.has_resume()


class SavedCandidateSearch(models.Model):
    """A saved candidate search for recruiters with basic notification tracking."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_candidate_searches')
    skills = models.CharField(max_length=500, blank=True)
    location = models.CharField(max_length=200, blank=True)
    projects = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_checked_at = models.DateTimeField(blank=True, null=True)
    last_notified_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        parts = []
        if self.skills:
            parts.append(f"skills={self.skills}")
        if self.location:
            parts.append(f"location={self.location}")
        if self.projects:
            parts.append(f"projects={self.projects}")
        summary = ', '.join(parts) or 'all profiles'
        return f"Search by {self.user.username}: {summary}"
