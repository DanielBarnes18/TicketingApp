"""
Management command to reset and update the application data.
This will update groups, ticket types, and statuses according to
the latest definitions in setup.py.
"""
from django.core.management.base import BaseCommand
import sys
import os
from pathlib import Path

class Command(BaseCommand):
    help = 'Reset and update application data using setup.py script'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            dest='force',
            help='Force reset without confirmation prompt',
        )

    def handle(self, *args, **options):
        if not options['force']:
            self.stdout.write(self.style.WARNING(
                "WARNING: This will delete all existing groups, ticket types, and statuses "
                "and replace them with new values. Tickets with statuses or types "
                "that no longer exist will need to be updated manually.\n"
                "Type 'yes' to continue, or anything else to abort."
            ))
            user_input = input().lower()
            if user_input != 'yes':
                self.stdout.write(self.style.ERROR('Operation aborted.'))
                return

        self.stdout.write(self.style.NOTICE('Resetting application data...'))
        
        # Run the setup script
        setup_path = Path(__file__).parents[4] / 'setup.py'
        if not setup_path.exists():
            self.stdout.write(self.style.ERROR(f'Setup script not found at {setup_path}'))
            return
        
        # Import and run the setup functions directly
        sys.path.insert(0, str(setup_path.parent))
        
        try:
            # We need to set up Django environment
            import django
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myapp.settings')
            django.setup()
            
            # Import the setup functions
            from setup import create_statuses, create_types, create_groups, create_priorities
            
            # Reset the data
            create_statuses()
            create_types()
            create_groups()
            create_priorities()
            
            self.stdout.write(self.style.SUCCESS('Application data reset successfully!'))
            self.stdout.write(self.style.WARNING(
                "NOTE: You may need to update tickets that have statuses or types "
                "that no longer exist."
            ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error resetting data: {e}'))
            import traceback
            self.stdout.write(self.style.ERROR(traceback.format_exc())) 