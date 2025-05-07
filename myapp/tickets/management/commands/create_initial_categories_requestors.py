from django.core.management.base import BaseCommand
from tickets.models import TicketCategory, TicketRequestor

class Command(BaseCommand):
    help = 'Creates initial ticket categories and requestors'

    def handle(self, *args, **kwargs):
        # Create Categories
        categories = [
            'Analytics',
            'AR Requests',
            'Data Quality',
            'Engineering',
            'Industry Regs',
            'Strategy and Planning',
            'Tech',
            'Final Billing'
        ]

        for category_name in categories:
            TicketCategory.objects.get_or_create(name=category_name)
            self.stdout.write(self.style.SUCCESS(f'Created category: {category_name}'))

        # Create Requestors
        requestors = [
            'British Gas',
            'Teneo',
            'Internal'
        ]

        for requestor_name in requestors:
            TicketRequestor.objects.get_or_create(name=requestor_name)
            self.stdout.write(self.style.SUCCESS(f'Created requestor: {requestor_name}'))

        self.stdout.write(self.style.SUCCESS('Successfully created initial categories and requestors.')) 