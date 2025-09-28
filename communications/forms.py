from django import forms
from django.contrib.auth.models import User
from .models import Message


class MessageForm(forms.ModelForm):
    """Form for sending messages between users."""
    
    class Meta:
        model = Message
        fields = ['recipient', 'subject', 'body']
        widgets = {
            'recipient': forms.Select(attrs={
                'class': 'form-select',
                'placeholder': 'Select recipient'
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter message subject'
            }),
            'body': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Type your message here...'
            })
        }
    
    def __init__(self, *args, **kwargs):
        sender = kwargs.pop('sender', None)
        super().__init__(*args, **kwargs)
        
        # Filter recipients based on sender type
        if sender:
            if hasattr(sender, 'user_profile') and sender.user_profile.is_recruiter():
                # Recruiters can message job seekers
                self.fields['recipient'].queryset = User.objects.filter(
                    user_profile__user_type='job_seeker'
                ).exclude(id=sender.id)
            elif hasattr(sender, 'user_profile') and sender.user_profile.is_job_seeker():
                # Job seekers can message recruiters
                self.fields['recipient'].queryset = User.objects.filter(
                    user_profile__user_type='recruiter'
                ).exclude(id=sender.id)
            else:
                # Fallback - show all users except sender
                self.fields['recipient'].queryset = User.objects.exclude(id=sender.id)
        
        # Add help text
        self.fields['recipient'].help_text = "Select the person you want to message"
        self.fields['subject'].help_text = "Brief subject line for your message"
        self.fields['body'].help_text = "Your message content"
    
    def clean_body(self):
        body = self.cleaned_data.get('body', '').strip()
        if len(body) < 10:
            raise forms.ValidationError("Message must be at least 10 characters long.")
        return body
