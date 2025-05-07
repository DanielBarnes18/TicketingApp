"""
Data migration to update tickets with new statuses and types.
"""
from django.db import migrations

def update_tickets(apps, schema_editor):
    """
    Update tickets with default values for statuses and types that may have been removed.
    """
    Ticket = apps.get_model('tickets', 'Ticket')
    TicketStatus = apps.get_model('tickets', 'TicketStatus')
    TicketType = apps.get_model('tickets', 'TicketType')
    
    # Get default status and type (or create them if they don't exist)
    default_status, _ = TicketStatus.objects.get_or_create(
        name='New',
        defaults={
            'description': 'A new ticket that has not been assigned or worked on yet.',
            'color': '#6c757d',
            'order': 10
        }
    )
    
    default_type, _ = TicketType.objects.get_or_create(
        name='Task',
        defaults={
            'description': 'A task that needs to be completed.'
        }
    )
    
    # Update tickets with null status or type
    tickets_updated = 0
    for ticket in Ticket.objects.all():
        updated = False
        
        if ticket.status is None:
            ticket.status = default_status
            updated = True
            
        if ticket.type is None:
            ticket.type = default_type
            updated = True
            
        if updated:
            ticket.save(update_fields=['status', 'type'])
            tickets_updated += 1
    
    print(f"Updated {tickets_updated} tickets with default values")


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0001_initial'),  # Adjust this to match your last migration
    ]

    operations = [
        migrations.RunPython(update_tickets, reverse_code=migrations.RunPython.noop),
    ] 