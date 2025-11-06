from .models import Message


def unread_messages(request):
    """Context processor to add unread message count to all templates."""
    if request.user.is_authenticated:
        unread_count = Message.objects.filter(
            recipient=request.user,
            read_at__isnull=True
        ).count()
        return {'unread_messages_count': unread_count}
    return {'unread_messages_count': 0}

