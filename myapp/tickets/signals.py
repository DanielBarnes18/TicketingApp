from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Ticket, TicketHistory, TicketStatus

@receiver(pre_save, sender=Ticket)
def track_ticket_changes(sender, instance, **kwargs):
    """Track changes to tickets for the history log."""
    # Only run if the ticket already exists
    if not instance.pk:
        return
        
    try:
        # Get the old instance
        old_instance = sender.objects.get(pk=instance.pk)
        
        # No need to do anything if the instance is the same
        if old_instance == instance:
            return
            
    except sender.DoesNotExist:
        # If the instance doesn't exist yet, it's new
        return

@receiver(post_save, sender=Ticket)
def set_initial_status(sender, instance, created, **kwargs):
    """Set the initial status of a new ticket."""
    if created and not instance.status:
        # Set initial status (typically "New" or "Open")
        if TicketStatus.objects.exists():
            initial_status = TicketStatus.objects.order_by('order').first()
            instance.status = initial_status
            instance.save(update_fields=['status']) 