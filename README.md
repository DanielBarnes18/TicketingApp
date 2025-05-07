# Ticketing System

A Django-based ticketing system for managing and tracking issues, similar to Jira.

## Features

- User authentication and registration
- User groups management for team organization
- Ticket creation and management
- Comment and attachment support for tickets
- Ticket assignment to users or groups
- Ticket statuses, priorities, and types
- Email notifications (configurable)
- Comprehensive ticket filtering
- Ticket history tracking
- REST API for integration with other systems
- Dashboard with ticket statistics

## Installation

### Requirements

- Python 3.8+
- Django 5.2+
- Other dependencies in requirements.txt

### Setup

1. Clone the repository:
   ```
   git clone <repository-url>
   cd ticketing
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run migrations:
   ```
   cd myapp
   python manage.py makemigrations
   python manage.py migrate
   ```

5. Create initial data:
   ```
   python setup.py
   ```
   This creates default statuses, priorities, types, groups, and a superuser (admin/adminpassword).

6. Start the development server:
   ```
   python manage.py runserver
   ```

7. Visit http://127.0.0.1:8000 in your browser.

## Usage

### User Types

- **Regular Users**: Can create tickets, comment, view their own tickets, and tickets assigned to them
- **Group Members**: Can view and update tickets assigned to their groups
- **Administrators**: Full access to all functionality including user and group management

### Key Features

- **Dashboard**: Displays overview of ticket statistics and recent tickets
- **Ticket List**: Shows all accessible tickets with filtering options
- **Ticket Detail**: Comprehensive view of a ticket with comments, attachments, and history
- **User Profile**: Manage your user information

### API Access

The system provides a REST API for programmatic access:

- API endpoint: `/api/v1/`
- API authentication: Token-based (`/api-token-auth/`)
- API documentation (Swagger UI): `/api/docs/` (if configured)

Example API usage:
```python
import requests

# Authenticate and get token
response = requests.post(
    'http://localhost:8000/api-token-auth/',
    data={'username': 'admin', 'password': 'adminpassword'}
)
token = response.json()['token']

# Use token to access API
headers = {'Authorization': f'Token {token}'}
tickets = requests.get('http://localhost:8000/api/v1/tickets/', headers=headers)
print(tickets.json())
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
