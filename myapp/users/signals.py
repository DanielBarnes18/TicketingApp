from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group
from .models import User

@receiver(post_save, sender=User)
def assign_default_group(sender, instance, created, **kwargs):
    """Assign newly created users to a default group if it exists."""
    if created:
        default_group, created = Group.objects.get_or_create(name='General Users')
        instance.groups.add(default_group) 