# Ticketing System

A Django-based ticketing system for managing and tracking support issues, bug reports, and feature requests. This application helps teams organize their workflow by enabling them to create, assign, and track tickets throughout their lifecycle.

## Project Overview

This ticketing system provides a comprehensive solution similar to Jira or other issue tracking platforms. It allows organizations to:

- Manage support requests from users or customers
- Track bugs and feature requests for software development
- Assign tasks to team members with appropriate deadlines
- Monitor the progress of issues through customizable statuses
- Generate reports and analytics on ticket resolution times and team performance

## Key Features

- **User Authentication & Authorization**: Secure login, registration, and role-based permissions
- **Team Organization**: User groups for team management and ticket assignment
- **Rich Ticket Management**:
  - Create, update, and close tickets with detailed information
  - Attach files for additional context (screenshots, logs, etc.)
  - Add comments for team collaboration
  - Track ticket history and changes
- **Flexible Configuration**:
  - Customizable ticket statuses (Open, In Progress, Resolved, etc.)
  - Priority levels for issue urgency
  - Categorization by ticket types (Bug, Feature Request, Support, etc.)
- **Notifications**: Email alerts for ticket updates and assignments
- **Search & Filtering**: Comprehensive ticket filtering to find relevant issues
- **Reporting Dashboard**: Visualization of ticket statistics and team performance
- **API Integration**: REST API for connecting with other systems

## Technical Details

### Requirements

- Python 3.8+
- Django 5.2+
- PostgreSQL database (recommended for production)
- Other dependencies in requirements.txt

### Deployment on Render

This application is configured for deployment on Render. Key deployment considerations:

1. PostgreSQL database setup on Render
2. Static files served using WhiteNoise
3. Environment variables for secure configuration
4. Build script for automated deployment

### Installation & Setup

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

## Usage Guide

### User Types and Permissions

- **Regular Users**: Can create tickets, comment, view their own tickets, and tickets assigned to them
- **Group Members**: Can view and update tickets assigned to their groups
- **Administrators**: Full access to all functionality including user and group management

### Common Workflows

1. **Creating a Ticket**: Users can submit new issues with details about the problem
2. **Assigning Tickets**: Team leads can assign tickets to appropriate team members
3. **Updating Status**: Assignees update ticket progress as they work on issues
4. **Adding Comments**: Team members can collaborate through ticket comments
5. **Resolving Tickets**: Once fixed, tickets can be marked as resolved or closed

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
