from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q
from .models import Message
from .forms import MessageForm


@login_required
def index(request):
    """Display user's messages (sent and received)."""
    user_messages = Message.objects.filter(
        Q(sender=request.user) | Q(recipient=request.user)
    ).order_by('-sent_at')
    
    # Separate sent and received messages
    sent_messages = user_messages.filter(sender=request.user)
    received_messages = user_messages.filter(recipient=request.user)
    
    # Count unread messages
    unread_count = received_messages.filter(read_at__isnull=True).count()
    
    context = {
        'template_data': {'title': 'Communications - HireBuzz'},
        'sent_messages': sent_messages,
        'received_messages': received_messages,
        'unread_count': unread_count,
    }
    return render(request, 'communications/index.html', context)


@login_required
def send_message(request):
    """Send a new message."""
    if request.method == 'POST':
        form = MessageForm(request.POST, sender=request.user)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.save()
            
            # Send email notification to recipient
            try:
                send_mail(
                    subject=f"New message from {request.user.get_full_name() or request.user.username}",
                    message=f"You have received a new message:\n\nSubject: {message.subject}\n\n{message.body}\n\nReply at: {request.build_absolute_uri('/communications/')}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[message.recipient.email],
                    fail_silently=False,
                )
                messages.success(request, f'Message sent to {message.recipient.get_full_name() or message.recipient.username}!')
            except Exception as e:
                # Message saved but email failed
                messages.warning(request, f'Message sent but email notification failed: {str(e)}')
            
            return redirect('communications:index')
    else:
        # Pre-select recipient if provided in URL
        initial_data = {}
        recipient_id = request.GET.get('recipient')
        if recipient_id:
            try:
                from django.contrib.auth.models import User
                recipient = User.objects.get(id=recipient_id)
                initial_data['recipient'] = recipient
            except User.DoesNotExist:
                pass
        
        form = MessageForm(sender=request.user, initial=initial_data)
    
    context = {
        'template_data': {'title': 'Send Message - HireBuzz'},
        'form': form,
    }
    return render(request, 'communications/send_message.html', context)


@login_required
def view_message(request, message_id):
    """View a specific message."""
    message = get_object_or_404(Message, id=message_id)
    
    # Check if user is sender or recipient
    if message.sender != request.user and message.recipient != request.user:
        messages.error(request, 'You do not have permission to view this message.')
        return redirect('communications:index')
    
    # Mark as read if user is the recipient
    if message.recipient == request.user and not message.is_read():
        message.mark_as_read()
    
    context = {
        'template_data': {'title': f'Message: {message.subject} - HireBuzz'},
        'message': message,
    }
    return render(request, 'communications/view_message.html', context)


@login_required
def reply_message(request, message_id):
    """Reply to a specific message."""
    original_message = get_object_or_404(Message, id=message_id)
    
    # Check if user is the recipient of the original message
    if original_message.recipient != request.user:
        messages.error(request, 'You can only reply to messages sent to you.')
        return redirect('communications:index')
    
    if request.method == 'POST':
        form = MessageForm(request.POST, sender=request.user)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.sender = request.user
            reply.recipient = original_message.sender
            reply.subject = f"Re: {original_message.subject}"
            reply.save()
            
            # Send email notification
            try:
                send_mail(
                    subject=f"Reply from {request.user.get_full_name() or request.user.username}",
                    message=f"You have received a reply:\n\nSubject: {reply.subject}\n\n{reply.body}\n\nReply at: {request.build_absolute_uri('/communications/')}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[reply.recipient.email],
                    fail_silently=False,
                )
                messages.success(request, f'Reply sent to {reply.recipient.get_full_name() or reply.recipient.username}!')
            except Exception as e:
                messages.warning(request, f'Reply sent but email notification failed: {str(e)}')
            
            return redirect('communications:index')
    else:
        # Pre-fill form with reply details
        form = MessageForm(sender=request.user, initial={
            'recipient': original_message.sender,
            'subject': f"Re: {original_message.subject}",
        })
    
    context = {
        'template_data': {'title': f'Reply to: {original_message.subject} - HireBuzz'},
        'form': form,
        'original_message': original_message,
    }
    return render(request, 'communications/reply_message.html', context)
