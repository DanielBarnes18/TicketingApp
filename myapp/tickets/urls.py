from django.urls import path, include
from . import views

# Main URL patterns for web views
urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('tickets/', views.TicketListView.as_view(), name='ticket-list'),
    path('tickets/kanban/', views.kanban_board, name='ticket-kanban'),
    path('tickets/new/', views.TicketCreateView.as_view(), name='ticket-create'),
    path('tickets/<int:pk>/', views.TicketDetailView.as_view(), name='ticket-detail'),
    path('tickets/<int:pk>/edit/', views.TicketUpdateView.as_view(), name='ticket-update'),
    path('tickets/<int:pk>/comment/', views.add_comment, name='add-comment'),
    path('tickets/<int:pk>/attachment/', views.add_attachment, name='add-attachment'),
    path('tickets/<int:pk>/status/<int:status_id>/', views.change_ticket_status, name='change-ticket-status'),
    path('groups/', views.group_management, name='group-management'),
    path('groups/create/', views.create_group, name='create-group'),
    path('groups/<int:pk>/delete/', views.delete_group, name='delete-group'),
]

# Internal API patterns for AJAX functionality
# Updated to match the URLs used in group_management.html
ajax_patterns = [
    path('groups/<int:pk>/members/', views.group_members, name='group-members'),
    path('groups/<int:pk>/members/add/', views.add_group_member, name='add-group-member'),
    path('groups/<int:pk>/members/<int:user_id>/remove/', views.remove_group_member, name='remove-group-member'),
    path('groups/<int:pk>/tickets/', views.group_tickets, name='group-tickets'),
    path('users/available/<int:group_id>/', views.available_users, name='available-users'),
]

# Add AJAX patterns to the main URL patterns
urlpatterns += ajax_patterns 