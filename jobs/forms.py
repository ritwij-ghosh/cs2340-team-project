from django import forms
from .models import Job


class JobForm(forms.ModelForm):
    """Form for creating and editing job postings."""

    class Meta:
        model = Job
        fields = [
            'title', 'company', 'location', 'latitude', 'longitude',
            'employment_type', 'experience_level',
            'work_type', 'skills_required', 'visa_sponsorship',
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
                'placeholder': 'e.g., Atlanta, GA or Remote',
                'id': 'id_location'
            }),
            'latitude': forms.HiddenInput(attrs={
                'id': 'id_latitude'
            }),
            'longitude': forms.HiddenInput(attrs={
                'id': 'id_longitude'
            }),
            'employment_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'experience_level': forms.Select(attrs={
                'class': 'form-select'
            }),
            'work_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'skills_required': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'e.g., Python, Django, React, PostgreSQL'
            }),
            'visa_sponsorship': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
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

    skills = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Skills (e.g., Python, Django, React)...'
        })
    )

    employment_type = forms.ChoiceField(
        choices=[('', 'Any Employment Type')] + Job.EMPLOYMENT_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    work_type = forms.ChoiceField(
        choices=[('', 'Any Work Type')] + Job.WORK_TYPE_CHOICES,
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

    # Salary range filters
    salary_min = forms.DecimalField(
        max_digits=10,
        decimal_places=0,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Min salary',
            'step': '1000'
        })
    )

    salary_max = forms.DecimalField(
        max_digits=10,
        decimal_places=0,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Max salary',
            'step': '1000'
        })
    )

    # Boolean filters
    visa_sponsorship = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )

    remote_only = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )

    # Commute radius filters
    enable_commute_filter = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'enable_commute_filter'
        })
    )

    commute_radius = forms.IntegerField(
        required=False,
        min_value=1,
        max_value=500,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Miles',
            'min': '1',
            'max': '500',
            'id': 'commute_radius_input'
        })
    )

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