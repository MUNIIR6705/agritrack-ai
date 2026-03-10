from .models import Notification
from django.db import DatabaseError

def notifications(request):
    """
    Context processor to show notifications in the navbar.
    Wrapped in try-except to prevent the "Blank Screen" crash if DB is not ready.
    """
    if request.user.is_authenticated:
        try:
            # Get the 5 most recent notifications
            navbar_notifs = Notification.objects.filter(
                user=request.user
            ).order_by('-date_created')[:5]
            
            # Count how many are unread
            unread_count = Notification.objects.filter(
                user=request.user, 
                is_read=False
            ).count()
            
            return {
                'navbar_notifications': navbar_notifs, 
                'unread_count': unread_count
            }
        except (DatabaseError, AttributeError):
            # If table doesn't exist or user isn't fully set up, return empty
            return {'navbar_notifications': [], 'unread_count': 0}
            
    return {'navbar_notifications': [], 'unread_count': 0}