from django import forms
from .models import Job


class JobForm(forms.ModelForm):
    """Form for creating and editing job postings."""

    class Meta:
        model = Job
        fields = [
            'title', 'company', 'location', 'employment_type', 'experience_level',
            'description', 'requirements', 'benefits', 'salary_min', 'salary_max',
            'status', 'application_deadline', 'external_url'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Senior Software Engineer'
            }),
            'company': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Company name'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Atlanta, GA or Remote'
            }),
            'employment_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'experience_level': forms.Select(attrs={
                'class': 'form-select'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Describe the role, responsibilities, and what the candidate will be doing...'
            }),
            'requirements': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'List required skills, experience, education, and qualifications...'
            }),
            'benefits': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Health insurance, 401k, flexible schedule, remote work options...'
            }),
            'salary_min': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Minimum salary',
                'step': '1000'
            }),
            'salary_max': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Maximum salary',
                'step': '1000'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'application_deadline': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'external_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://company.com/apply'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make certain fields required for better UX
        self.fields['title'].required = True
        self.fields['company'].required = True
        self.fields['location'].required = True
        self.fields['description'].required = True
        self.fields['requirements'].required = True

    def clean(self):
        cleaned_data = super().clean()
        salary_min = cleaned_data.get('salary_min')
        salary_max = cleaned_data.get('salary_max')

        # Validate salary range
        if salary_min and salary_max and salary_min > salary_max:
            raise forms.ValidationError(
                "Minimum salary cannot be greater than maximum salary."
            )

        return cleaned_data


class JobSearchForm(forms.Form):
    """Form for searching and filtering job listings."""

    search = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search job titles, companies, or keywords...'
        })
    )

    location = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Location'
        })
    )

    employment_type = forms.ChoiceField(
        choices=[('', 'Any Employment Type')] + Job.EMPLOYMENT_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    experience_level = forms.ChoiceField(
        choices=[('', 'Any Experience Level')] + Job.EXPERIENCE_LEVEL_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )