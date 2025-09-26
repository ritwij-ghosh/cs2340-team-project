from django.conf import settings
from django.db import models


class Application(models.Model):
    """Job application tracking for a job seeker."""

    class Status(models.TextChoices):
        APPLIED = 'applied', 'Applied'
        REVIEW = 'review', 'Review'
        INTERVIEW = 'interview', 'Interview'
        OFFER = 'offer', 'Offer'
        CLOSED = 'closed', 'Closed'

    STATUS_BADGE_CLASSES = {
        Status.APPLIED: 'bg-secondary text-dark',
        Status.REVIEW: 'bg-primary',
        Status.INTERVIEW: 'bg-warning text-dark',
        Status.OFFER: 'bg-success',
        Status.CLOSED: 'bg-danger'
    }

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='applications'
    )
    job_title = models.CharField(max_length=200)
    company_name = models.CharField(max_length=200)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.APPLIED
    )
    applied_on = models.DateField(auto_now_add=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        unique_together = ('user', 'job_title', 'company_name', 'applied_on')

    def __str__(self):
        return f"{self.job_title} at {self.company_name} ({self.get_status_display()})"

    @property
    def status_index(self) -> int:
        """Zero-based position of current status in the pipeline."""
        statuses = [choice[0] for choice in self.Status.choices]
        return statuses.index(self.status)

    @property
    def progress_percentage(self) -> int:
        """Return rough completion percentage for visual progress bars."""
        total_steps = len(self.Status.choices) - 1
        if total_steps <= 0:
            return 0
        return int((self.status_index / total_steps) * 100)

    @property
    def status_badge_class(self) -> str:
        """Bootstrap class for displaying a colored badge for the current status."""
        return self.STATUS_BADGE_CLASSES.get(self.status, 'bg-secondary text-dark')
