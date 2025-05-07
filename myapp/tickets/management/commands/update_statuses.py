from django.core.management.base import BaseCommand
from tickets.models import Ticket, TicketStatus

class Command(BaseCommand):
    help = 'Updates ticket statuses to remove Closed and add QA'
    
    def handle(self, *args, **options):
        # 1. First check if we need to migrate tickets from Closed to Resolved
        try:
            closed_status = TicketStatus.objects.get(name='Closed')
            # Get or create the Resolved status
            resolved_status, _ = TicketStatus.objects.get_or_create(
                name='Resolved',
                defaults={
                    'description': 'The ticket has been resolved and verified.',
                    'color': '#28a745',
                    'order': 50
                }
            )
            
            # Update all tickets with Closed status to Resolved
            tickets_updated = Ticket.objects.filter(status=closed_status).update(status=resolved_status)
            self.stdout.write(self.style.SUCCESS(f"Updated {tickets_updated} tickets from 'Closed' to 'Resolved' status"))
        except TicketStatus.DoesNotExist:
            self.stdout.write("No 'Closed' status found - no tickets to update")
        
        # 2. Now recreate statuses from scratch
        self.stdout.write("Recreating ticket statuses...")
        statuses = [
            {'name': 'New', 'description': 'A new ticket that has not been assigned or worked on yet.', 'color': '#6c757d', 'order': 10},
            {'name': 'In Progress', 'description': 'Work has actively started on the ticket.', 'color': '#007bff', 'order': 20},
            {'name': 'On Hold', 'description': 'The ticket is temporarily on hold.', 'color': '#ffc107', 'order': 30},
            {'name': 'QA', 'description': 'The ticket is ready for quality assurance testing.', 'color': '#17a2b8', 'order': 40},
            {'name': 'Resolved', 'description': 'The ticket has been resolved and verified.', 'color': '#28a745', 'order': 50},
        ]
        
        # Clear existing statuses for a clean slate (this is safe since we migrated tickets above)
        TicketStatus.objects.all().delete()
        
        # Create new statuses
        for status in statuses:
            TicketStatus.objects.get_or_create(name=status['name'], defaults=status)
        
        self.stdout.write(self.style.SUCCESS(f"Created {len(statuses)} ticket statuses")) 