from django import forms

from applications.models import Application


class ApplicationForm(forms.ModelForm):
    """Form to create or edit a job application."""

    class Meta:
        model = Application
        fields = ['job_title', 'company_name', 'status', 'notes']
        widgets = {
            'job_title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Software Engineer'
            }),
            'company_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Acme Corp'
            }),
            'status': forms.Select(attrs={'class': 'form-select bg-dark text-light'}),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Optional notes, interview dates, recruiter comments...'
            }),
        }


class ApplicationStatusForm(forms.ModelForm):
    """Slim form to update status from list views."""

    class Meta:
        model = Application
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select form-select-sm bg-dark text-light'})
        }
