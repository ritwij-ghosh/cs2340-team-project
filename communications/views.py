from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.db.models import Q
from .models import EmailMessage
from .forms import SendEmailForm, QuickEmailForm, EmailReplyForm


def index(request):
    """Main communications dashboard."""
    if request.user.is_authenticated:
        # Get user's emails
        sent_emails = EmailMessage.objects.filter(sender=request.user).order_by('-sent_at')[:5]
        received_emails = EmailMessage.objects.filter(recipient=request.user).order_by('-sent_at')[:5]
        unread_count = EmailMessage.objects.filter(recipient=request.user, is_read=False).count()
        
        context = {
            'sent_emails': sent_emails,
            'received_emails': received_emails,
            'unread_count': unread_count,
            'template_data': {'title': 'Communications - HireBuzz'}
        }
    else:
        context = {
            'template_data': {'title': 'Communications - HireBuzz'}
        }
    
    return render(request, 'communications/index.html', context)


@login_required
def send_email(request):
    """Send email to a candidate."""
    if request.method == 'POST':
        form = SendEmailForm(request.POST)
        if form.is_valid():
            email = form.save(commit=False)
            email.sender = request.user
            
            # Send the actual email
            try:
                send_mail(
                    subject=email.subject,
                    message=email.message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email.recipient.email],
                    fail_silently=False,
                )
                email.save()
                messages.success(request, f'Email sent successfully to {email.recipient.get_full_name() or email.recipient.username}!')
                return redirect('communications:email_list')
            except Exception as e:
                messages.error(request, f'Failed to send email: {str(e)}')
    else:
        form = SendEmailForm()
    
    context = {
        'form': form,
        'template_data': {'title': 'Send Email - HireBuzz'}
    }
    return render(request, 'communications/send_email.html', context)


@login_required
def send_quick_email(request, user_id):
    """Send quick email to a specific candidate from their profile."""
    recipient = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        form = QuickEmailForm(request.POST)
        if form.is_valid():
            # Create email message
            email = EmailMessage(
                sender=request.user,
                recipient=recipient,
                subject=form.cleaned_data['subject'],
                message=form.cleaned_data['message'],
                email_type=form.cleaned_data['email_type'],
                job_title=form.cleaned_data.get('job_title', ''),
                company_name=form.cleaned_data.get('company_name', '')
            )
            
            # Send the actual email
            try:
                send_mail(
                    subject=email.subject,
                    message=email.message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email.recipient.email],
                    fail_silently=False,
                )
                email.save()
                messages.success(request, f'Email sent successfully to {recipient.get_full_name() or recipient.username}!')
                return redirect('profiles:view', user_id=user_id)
            except Exception as e:
                messages.error(request, f'Failed to send email: {str(e)}')
    else:
        form = QuickEmailForm()
    
    context = {
        'form': form,
        'recipient': recipient,
        'template_data': {'title': f'Send Email to {recipient.username} - HireBuzz'}
    }
    return render(request, 'communications/send_quick_email.html', context)


@login_required
def email_list(request):
    """List all emails for the current user."""
    emails = EmailMessage.objects.filter(
        Q(sender=request.user) | Q(recipient=request.user)
    ).order_by('-sent_at')
    
    context = {
        'emails': emails,
        'template_data': {'title': 'Email Messages - HireBuzz'}
    }
    return render(request, 'communications/email_list.html', context)


@login_required
def email_detail(request, email_id):
    """View details of a specific email."""
    email = get_object_or_404(EmailMessage, id=email_id)
    
    # Check if user has permission to view this email
    if email.sender != request.user and email.recipient != request.user:
        messages.error(request, 'You do not have permission to view this email.')
        return redirect('communications:email_list')
    
    # Mark as read if user is the recipient
    if email.recipient == request.user and not email.is_read:
        email.mark_as_read()
    
    # Handle reply
    if request.method == 'POST' and 'reply' in request.POST:
        reply_form = EmailReplyForm(request.POST)
        if reply_form.is_valid():
            # Create reply email
            reply_email = EmailMessage(
                sender=request.user,
                recipient=email.sender if request.user == email.recipient else email.recipient,
                subject=f"Re: {email.subject}",
                message=reply_form.cleaned_data['message'],
                email_type='follow_up'
            )
            
            try:
                send_mail(
                    subject=reply_email.subject,
                    message=reply_email.message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[reply_email.recipient.email],
                    fail_silently=False,
                )
                reply_email.save()
                messages.success(request, 'Reply sent successfully!')
                return redirect('communications:email_detail', email_id=email_id)
            except Exception as e:
                messages.error(request, f'Failed to send reply: {str(e)}')
    else:
        reply_form = EmailReplyForm(original_subject=email.subject)
    
    context = {
        'email': email,
        'reply_form': reply_form,
        'template_data': {'title': f'{email.subject} - HireBuzz'}
    }
    return render(request, 'communications/email_detail.html', context)
