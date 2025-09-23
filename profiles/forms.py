from django import forms
from django.contrib.auth.models import User
from .models import Profile


class ProfileForm(forms.ModelForm):
    """Form for creating and editing job seeker profiles."""
    
    class Meta:
        model = Profile
        fields = [
            'headline', 'bio', 'location', 'phone',
            'skills', 'education', 'work_experience',
            'linkedin_url', 'github_url', 'portfolio_url', 'other_url',
            'is_public', 'show_bio', 'show_location', 'show_phone',
            'show_education', 'show_work_experience', 'show_links'
        ]
        widgets = {
            'headline': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Senior Software Engineer'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Tell us about yourself and your career goals...'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Atlanta, GA'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., (555) 123-4567'
            }),
            'skills': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'List your key skills separated by commas (e.g., Python, Django, React, SQL)'
            }),
            'education': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'List your educational background (e.g., BS Computer Science - Georgia Tech, 2023)'
            }),
            'work_experience': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Describe your work experience, including company names, positions, and key achievements'
            }),
            'linkedin_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://linkedin.com/in/yourname'
            }),
            'github_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://github.com/yourname'
            }),
            'portfolio_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://yourportfolio.com'
            }),
            'other_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://yourblog.com or other relevant URL'
            }),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'show_bio': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'show_location': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'show_phone': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'show_education': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'show_work_experience': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'show_links': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        help_texts = {
            'headline': 'A brief professional headline that describes your role or expertise',
            'bio': 'A brief description about yourself and your career goals',
            'skills': 'List your key skills separated by commas',
            'education': 'List your educational background',
            'work_experience': 'Describe your work experience with key achievements',
            'linkedin_url': 'Your LinkedIn profile URL',
            'github_url': 'Your GitHub profile URL',
            'portfolio_url': 'Your portfolio or personal website URL',
            'other_url': 'Any other relevant URL (e.g., personal blog, Stack Overflow)',
            'is_public': 'Untick this if you want to hide your entire profile from recruiters.',
            'show_bio': 'Control whether your bio appears on your public profile.',
            'show_location': 'Control whether your location appears on your public profile.',
            'show_phone': 'Allow recruiters to see your phone number.',
            'show_education': 'Control whether your education history appears on your public profile.',
            'show_work_experience': 'Control whether your work experience appears on your public profile.',
            'show_links': 'Control whether your professional links appear on your public profile.',
        }
    
    def clean_skills(self):
        """Clean and validate skills input."""
        skills = self.cleaned_data.get('skills', '')
        if skills:
            # Remove extra whitespace and empty entries
            skills_list = [skill.strip() for skill in skills.split(',') if skill.strip()]
            if not skills_list:
                raise forms.ValidationError("Please enter at least one skill.")
            return ', '.join(skills_list)
        return skills
    
    def clean_education(self):
        """Clean and validate education input."""
        education = self.cleaned_data.get('education', '')
        if not education.strip():
            raise forms.ValidationError("Please provide your educational background.")
        return education.strip()
    
    def clean_work_experience(self):
        """Clean and validate work experience input."""
        work_experience = self.cleaned_data.get('work_experience', '')
        if not work_experience.strip():
            raise forms.ValidationError("Please provide your work experience.")
        return work_experience.strip()


class UserForm(forms.ModelForm):
    """Form for updating user basic information."""
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
