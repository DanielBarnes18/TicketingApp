#!/usr/bin/env python
"""
Script to set up initial data for the ticketing system.
Run this after migrations to create necessary seed data.
"""

import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from tickets.models import TicketStatus, TicketPriority, TicketType

User = get_user_model()

def create_statuses():
    """Create default ticket statuses."""
    statuses = [
        {'name': 'New', 'description': 'A new ticket that has not been assigned or worked on yet.', 'color': '#6c757d', 'order': 10},
        {'name': 'In Progress', 'description': 'Work has actively started on the ticket.', 'color': '#007bff', 'order': 20},
        {'name': 'On Hold', 'description': 'The ticket is temporarily on hold.', 'color': '#ffc107', 'order': 30},
        {'name': 'QA', 'description': 'The ticket is ready for quality assurance testing.', 'color': '#17a2b8', 'order': 40},
        {'name': 'Resolved', 'description': 'The ticket has been resolved and verified.', 'color': '#28a745', 'order': 50},
    ]
    
    # Clear existing statuses for a clean slate
    TicketStatus.objects.all().delete()
    
    for status in statuses:
        TicketStatus.objects.get_or_create(name=status['name'], defaults=status)
    
    print(f"Created {len(statuses)} ticket statuses")

def create_priorities():
    """Create default ticket priorities."""
    priorities = [
        {'name': 'Low', 'description': 'Minor issues that do not impact business operations.', 'color': '#28a745', 'order': 10},
        {'name': 'Medium', 'description': 'Issues with limited impact to business operations.', 'color': '#17a2b8', 'order': 20},
        {'name': 'High', 'description': 'Issues with significant impact to business operations.', 'color': '#ffc107', 'order': 30},
        {'name': 'Critical', 'description': 'Severe issues that prevent business operations.', 'color': '#dc3545', 'order': 40},
    ]
    
    for priority in priorities:
        TicketPriority.objects.get_or_create(name=priority['name'], defaults=priority)
    
    print(f"Created {len(priorities)} ticket priorities")

def create_types():
    """Create default ticket types."""
    types = [
        {'name': 'Task', 'description': 'A task that needs to be completed.'},
        {'name': 'Report', 'description': 'Report generation or analysis task.'},
        {'name': 'Support', 'description': 'A support request or question.'},
        {'name': 'Bug', 'description': 'Something is not working as expected.'},
    ]
    
    # Clear existing types for a clean slate
    TicketType.objects.all().delete()
    
    for ticket_type in types:
        TicketType.objects.get_or_create(name=ticket_type['name'], defaults=ticket_type)
    
    print(f"Created {len(types)} ticket types")

def create_groups():
    """Create default user groups."""
    groups = [
        {'name': 'General Users', 'description': 'Regular system users'},
        {'name': 'QA', 'description': 'Quality assurance team'},
        {'name': 'Analytics', 'description': 'Data analysis team'},
        {'name': 'Data Engineering', 'description': 'Data engineering team'},
        {'name': 'Billing Operations', 'description': 'Billing operations team'},
        {'name': 'Collections', 'description': 'Collections team'},
        {'name': 'Administration', 'description': 'System administrators'},
        {'name': 'Automation', 'description': 'Automation engineering team'},
    ]
    
    # Clear existing groups for a clean slate
    Group.objects.all().delete()
    
    for group_info in groups:
        group, created = Group.objects.get_or_create(name=group_info['name'])
        
    print(f"Created {len(groups)} user groups")

def create_superuser():
    """Create a superuser if none exists."""
    if not User.objects.filter(is_superuser=True).exists():
        User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpassword',
            first_name='Admin',
            last_name='User'
        )
        print("Created superuser 'admin' with password 'adminpassword'")
    else:
        print("Superuser already exists")

if __name__ == '__main__':
    print("Setting up initial data for ticketing system...")
    create_statuses()
    create_priorities()
    create_types()
    create_groups()
    create_superuser()
    print("Setup complete!") 