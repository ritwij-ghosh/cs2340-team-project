from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Job(models.Model):
    """Job posting model for recruiters to post and manage job openings."""

    EMPLOYMENT_TYPE_CHOICES = [
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('internship', 'Internship'),
        ('temporary', 'Temporary'),
    ]

    EXPERIENCE_LEVEL_CHOICES = [
        ('entry', 'Entry Level'),
        ('mid', 'Mid Level'),
        ('senior', 'Senior Level'),
        ('executive', 'Executive'),
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('closed', 'Closed'),
    ]

    # Job basic information
    title = models.CharField(
        max_length=200,
        help_text="Job title (e.g., 'Senior Software Engineer')"
    )
    company = models.CharField(
        max_length=200,
        help_text="Company name"
    )
    location = models.CharField(
        max_length=100,
        help_text="Job location (e.g., 'Atlanta, GA' or 'Remote')"
    )
    employment_type = models.CharField(
        max_length=20,
        choices=EMPLOYMENT_TYPE_CHOICES,
        default='full_time'
    )
    experience_level = models.CharField(
        max_length=20,
        choices=EXPERIENCE_LEVEL_CHOICES,
        default='mid'
    )

    # Job details
    description = models.TextField(
        help_text="Detailed job description including responsibilities and requirements"
    )
    requirements = models.TextField(
        help_text="Required skills, experience, and qualifications"
    )
    benefits = models.TextField(
        blank=True,
        help_text="Benefits and perks offered (optional)"
    )

    # Compensation
    salary_min = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Minimum salary (optional)"
    )
    salary_max = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Maximum salary (optional)"
    )

    # Job management
    recruiter = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posted_jobs'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )

    # Application settings
    application_deadline = models.DateField(
        null=True,
        blank=True,
        help_text="Application deadline (optional)"
    )
    external_url = models.URLField(
        blank=True,
        help_text="External application URL (optional)"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} at {self.company}"

    def get_absolute_url(self):
        return reverse('jobs:detail', kwargs={'pk': self.pk})

    def is_active(self):
        """Check if job is currently active."""
        return self.status == 'active'

    def has_salary_range(self):
        """Check if job has salary information."""
        return self.salary_min is not None or self.salary_max is not None

    def get_salary_display(self):
        """Return formatted salary range or indication if not specified."""
        if self.salary_min and self.salary_max:
            return f"${self.salary_min:,.0f} - ${self.salary_max:,.0f}"
        elif self.salary_min:
            return f"${self.salary_min:,.0f}+"
        elif self.salary_max:
            return f"Up to ${self.salary_max:,.0f}"
        return "Salary not specified"