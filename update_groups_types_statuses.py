#!/usr/bin/env python
"""
Script to update the groups, ticket types, and statuses in the system.
This will:
1. Update tickets with null references to use defaults
2. Delete and recreate all groups, statuses, and ticket types
"""
import os
import sys
import subprocess
from pathlib import Path

# Add the myapp directory to the Python path
myapp_path = Path(__file__).resolve().parent / "myapp"
sys.path.append(str(myapp_path.parent))

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myapp.config.settings')
django.setup()

def main():
    print("===== Updating Groups, Types, and Statuses =====")
    print("This script will update your ticketing system with the new configuration.")
    print("\nStep 1: Checking for any tickets that need updating...")
    
    # First run the data migration to handle any tickets with soon-to-be-deleted statuses/types
    try:
        subprocess.check_call([sys.executable, 'myapp/manage.py', 'migrate', 'tickets'])
        print("✓ Migration successful")
    except subprocess.CalledProcessError:
        print("✗ Migration failed")
        return
    
    print("\nStep 2: Resetting and updating application data...")
    
    # Run our setup script directly
    try:
        # Import and run setup functions directly
        from myapp.setup import create_statuses, create_types, create_groups, create_priorities
        
        # Reset the data
        create_statuses()
        create_types()
        create_groups()
        create_priorities()
        
        print("✓ Data update successful")
    except Exception as e:
        print(f"✗ Data update failed: {e}")
        import traceback
        print(traceback.format_exc())
        return
    
    print("\n===== Update Complete =====")
    print("The following entities have been updated:")
    print("  - Groups: 'General Users', 'QA', 'Analytics', 'Data Engineering', 'Billing Operations', 'Collections', 'Administration', 'Automation'")
    print("  - Types: 'Task', 'Report', 'Support', 'Bug'")
    print("  - Statuses: 'New', 'In Progress', 'On Hold', 'QA', 'Resolved'")
    print("\nPlease check any existing tickets to ensure they have valid statuses and types.")

if __name__ == "__main__":
    main() 