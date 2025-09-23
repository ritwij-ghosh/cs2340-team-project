from django import forms
from django.contrib.auth.models import User
from .models import EmailMessage


class SendEmailForm(forms.ModelForm):
    """Form for sending emails to candidates."""
    
    class Meta:
        model = EmailMessage
        fields = ['recipient', 'subject', 'message', 'email_type', 'job_title', 'company_name']
        widgets = {
            'recipient': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': 'Select a candidate'
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter email subject'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 8,
                'placeholder': 'Write your message here...'
            }),
            'email_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'job_title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Job title (optional)'
            }),
            'company_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Company name (optional)'
            }),
        }
        help_texts = {
            'recipient': 'Select the candidate you want to email',
            'subject': 'A clear, descriptive subject line',
            'message': 'Your message to the candidate',
            'email_type': 'Type of communication',
            'job_title': 'If this email is about a specific job',
            'company_name': 'If this email is from a specific company',
        }
    
    def __init__(self, *args, **kwargs):
        # Get only users who have profiles (candidates)
        super().__init__(*args, **kwargs)
        self.fields['recipient'].queryset = User.objects.filter(profile__isnull=False).order_by('username')
        self.fields['recipient'].empty_label = "Select a candidate..."
        
        # Make job_title and company_name optional
        self.fields['job_title'].required = False
        self.fields['company_name'].required = False


class QuickEmailForm(forms.Form):
    """Quick email form for sending emails from profile pages."""
    
    subject = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter email subject'
        }),
        help_text="A clear, descriptive subject line"
    )
    
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 6,
            'placeholder': 'Write your message here...'
        }),
        help_text="Your message to the candidate"
    )
    
    email_type = forms.ChoiceField(
        choices=EmailMessage.EMAIL_TYPES,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        initial='general',
        help_text="Type of communication"
    )
    
    job_title = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Job title (optional)'
        }),
        help_text="If this email is about a specific job"
    )
    
    company_name = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Company name (optional)'
        }),
        help_text="If this email is from a specific company"
    )


class EmailReplyForm(forms.Form):
    """Form for replying to emails."""
    
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 6,
            'placeholder': 'Write your reply here...'
        }),
        help_text="Your reply message"
    )
    
    def __init__(self, *args, **kwargs):
        original_subject = kwargs.pop('original_subject', '')
        super().__init__(*args, **kwargs)
        if original_subject and not original_subject.startswith('Re: '):
            self.fields['subject'] = forms.CharField(
                initial=f"Re: {original_subject}",
                widget=forms.TextInput(attrs={
                    'class': 'form-control',
                    'readonly': True
                })
            )
