from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import UserProfile

@receiver(post_save, sender=User)
def create_health_profile(sender, instance, created, **kwargs):
    """Automatically create a UserProfile when a new User is registered."""
    if created:
        UserProfile.objects.create(
            user=instance,
            farm_name=f"{instance.username.title()}'s Farm" # Optional default
        )

@receiver(post_save, sender=User)
def save_health_profile(sender, instance, **kwargs):
    """Ensure the profile is saved whenever the user object is saved."""
    if hasattr(instance, 'health_profile'):
        instance.health_profile.save()