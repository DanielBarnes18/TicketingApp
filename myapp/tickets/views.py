from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.db.models import Q
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.http import JsonResponse
from django.contrib.auth.models import Group
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST
from django.contrib.auth import get_user_model
import json

from .models import (
    Ticket, TicketStatus, TicketPriority, TicketType,
    TicketComment, TicketAttachment, TicketHistory, TicketCategory, TicketRequestor
)
from .forms import (
    TicketForm, TicketCommentForm, TicketAttachmentForm, TicketFilterForm
)

# Get the custom User model
User = get_user_model()

class TicketListView(LoginRequiredMixin, ListView):
    """Display a list of tickets with filtering options."""
    model = Ticket
    template_name = 'tickets/ticket_list.html'
    context_object_name = 'tickets'
    paginate_by = 10
    
    def get_queryset(self):
        # Get base queryset
        queryset = super().get_queryset()
        
        # Apply filters from form
        form = TicketFilterForm(self.request.GET, user=self.request.user)
        
        if form.is_valid():
            # Filter by status
            if form.cleaned_data.get('status'):
                queryset = queryset.filter(status__in=form.cleaned_data['status'])
            
            # Filter by priority
            if form.cleaned_data.get('priority'):
                queryset = queryset.filter(priority__in=form.cleaned_data['priority'])
            
            # Filter by type
            if form.cleaned_data.get('type'):
                queryset = queryset.filter(type__in=form.cleaned_data['type'])
            
            # Filter by category
            if form.cleaned_data.get('category'):
                queryset = queryset.filter(category__in=form.cleaned_data['category'])
            
            # Filter by requestor
            if form.cleaned_data.get('requestor'):
                queryset = queryset.filter(requestor__in=form.cleaned_data['requestor'])
            
            # Filter by assigned group
            if form.cleaned_data.get('assigned_group'):
                queryset = queryset.filter(assigned_group__in=form.cleaned_data['assigned_group'])
            
            # Filter assigned to me
            if form.cleaned_data.get('assigned_to_me'):
                queryset = queryset.filter(assigned_to=self.request.user)
            
            # Filter created by me
            if form.cleaned_data.get('created_by_me'):
                queryset = queryset.filter(created_by=self.request.user)
            
            # Filter tickets with user comments
            if form.cleaned_data.get('user_comments'):
                queryset = queryset.filter(comments__author=self.request.user).distinct()
            
            # Search in title and description
            if form.cleaned_data.get('search'):
                search_term = form.cleaned_data['search']
                queryset = queryset.filter(
                    Q(title__icontains=search_term) | 
                    Q(description__icontains=search_term) |
                    Q(key_stakeholders__icontains=search_term)
                )
        
        # Removed the restriction that limited non-superuser's view
        # Now all users can see all tickets
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = TicketFilterForm(self.request.GET, user=self.request.user)
        return context

class TicketDetailView(LoginRequiredMixin, DetailView):
    """Display detailed information about a ticket."""
    model = Ticket
    template_name = 'tickets/ticket_detail.html'
    context_object_name = 'ticket'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = TicketCommentForm()
        context['attachment_form'] = TicketAttachmentForm()
        
        # Add available statuses for the status change buttons, excluding the current status and 'New' status
        new_status = TicketStatus.objects.filter(name='New').first()
        if self.object.status:
            # Exclude current status and 'New' status
            exclude_statuses = [self.object.status.id]
            if new_status:
                exclude_statuses.append(new_status.id)
            context['available_statuses'] = TicketStatus.objects.exclude(id__in=exclude_statuses)
        else:
            # Just exclude 'New' status
            if new_status:
                context['available_statuses'] = TicketStatus.objects.exclude(id=new_status.id)
            else:
                context['available_statuses'] = TicketStatus.objects.all()
        
        return context

class TicketCreateView(LoginRequiredMixin, CreateView):
    """Create a new ticket."""
    model = Ticket
    form_class = TicketForm
    template_name = 'tickets/ticket_form.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Ticket created successfully.')
        return super().form_valid(form)

class TicketUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Update an existing ticket."""
    model = Ticket
    form_class = TicketForm
    template_name = 'tickets/ticket_form.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def test_func(self):
        # Check if user can edit this ticket
        ticket = self.get_object()
        user = self.request.user
        
        # Allow if user is superuser, ticket creator, assignee, or in assigned group
        return (user.is_superuser or 
                ticket.created_by == user or 
                ticket.assigned_to == user or 
                (ticket.assigned_group and ticket.assigned_group in user.groups.all()))
    
    def form_valid(self, form):
        # Get the existing ticket
        ticket = self.get_object()
        
        # Check which fields have changed
        for field_name, field in form.fields.items():
            if field_name in form.changed_data:
                old_value = getattr(ticket, field_name)
                new_value = form.cleaned_data[field_name]
                
                # Handle ForeignKey fields
                if field_name in ['status', 'priority', 'type', 'assigned_to', 'assigned_group']:
                    if old_value:
                        old_display = str(old_value)
                    else:
                        old_display = "None"
                    
                    if new_value:
                        new_display = str(new_value)
                    else:
                        new_display = "None"
                else:
                    old_display = str(old_value)
                    new_display = str(new_value)
                
                # Create history entry
                TicketHistory.objects.create(
                    ticket=ticket,
                    changed_by=self.request.user,
                    field_name=field_name,
                    old_value=old_display,
                    new_value=new_display
                )
        
        messages.success(self.request, 'Ticket updated successfully.')
        return super().form_valid(form)

@login_required
def add_comment(request, pk):
    """Add a comment to a ticket."""
    ticket = get_object_or_404(Ticket, pk=pk)
    
    if request.method == 'POST':
        form = TicketCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.ticket = ticket
            comment.author = request.user
            comment.save()
            messages.success(request, 'Comment added successfully.')
            
            # For AJAX requests, return JSON response
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'comment': {
                        'author': comment.author.get_full_name() or comment.author.username,
                        'content': comment.content,
                        'created_at': comment.created_at.strftime('%b %d, %Y, %I:%M %p'),
                        'timestamp': int(comment.created_at.timestamp())
                    }
                })
            
    return redirect('ticket-detail', pk=ticket.pk)

@login_required
def add_attachment(request, pk):
    """Add an attachment to a ticket."""
    ticket = get_object_or_404(Ticket, pk=pk)
    
    if request.method == 'POST':
        form = TicketAttachmentForm(request.POST, request.FILES)
        if form.is_valid():
            attachment = form.save(commit=False)
            attachment.ticket = ticket
            attachment.uploaded_by = request.user
            attachment.save()
            messages.success(request, 'Attachment added successfully.')
    
    return redirect('ticket-detail', pk=ticket.pk)

@login_required
def dashboard(request):
    """Display the user's dashboard with relevant ticket information."""
    user = request.user
    user_groups = user.groups.all()
    
    # Get tickets assigned to the user
    assigned_tickets = Ticket.objects.filter(assigned_to=user)
    
    # Get tickets assigned to user's groups
    group_tickets = Ticket.objects.filter(assigned_group__in=user_groups).exclude(assigned_to=user)
    
    # Get tickets created by the user
    created_tickets = Ticket.objects.filter(created_by=user)
    
    # Counts by status
    status_counts = {
        'assigned': {},
        'group': {},
        'created': {}
    }
    
    for status in TicketStatus.objects.all():
        status_counts['assigned'][status.name] = assigned_tickets.filter(status=status).count()
        status_counts['group'][status.name] = group_tickets.filter(status=status).count()
        status_counts['created'][status.name] = created_tickets.filter(status=status).count()
    
    context = {
        'assigned_tickets': assigned_tickets.order_by('-updated_at')[:5],
        'group_tickets': group_tickets.order_by('-updated_at')[:5],
        'created_tickets': created_tickets.order_by('-updated_at')[:5],
        'status_counts': status_counts,
        'total_assigned': assigned_tickets.count(),
        'total_group': group_tickets.count(),
        'total_created': created_tickets.count(),
    }
    
    return render(request, 'tickets/dashboard.html', context)

@login_required
def change_ticket_status(request, pk, status_id):
    """Quick action to change a ticket's status."""
    ticket = get_object_or_404(Ticket, pk=pk)
    status = get_object_or_404(TicketStatus, pk=status_id)
    
    # Prevent changing to "New" status
    if status.name == 'New':
        messages.error(request, "Tickets cannot be changed back to 'New' status.")
        return redirect('ticket-detail', pk=ticket.pk)
    
    # Check permission
    user = request.user
    if not (user.is_superuser or 
            ticket.created_by == user or 
            ticket.assigned_to == user or 
            (ticket.assigned_group and ticket.assigned_group in user.groups.all())):
        messages.error(request, "You don't have permission to change this ticket's status.")
        return redirect('ticket-detail', pk=ticket.pk)
    
    # Record status change history
    old_status = ticket.status
    TicketHistory.objects.create(
        ticket=ticket,
        changed_by=request.user,
        field_name='status',
        old_value=old_status.name if old_status else 'None',
        new_value=status.name
    )
    
    # Auto-assign to QA group when status is changed to QA
    old_group = ticket.assigned_group
    if status.name == 'QA':
        # Find the QA group
        qa_group = Group.objects.filter(name__icontains='QA').first()
        
        if qa_group and ticket.assigned_group != qa_group:
            # Record group change history
            TicketHistory.objects.create(
                ticket=ticket,
                changed_by=request.user,
                field_name='assigned_group',
                old_value=str(old_group) if old_group else 'None',
                new_value=qa_group.name
            )
            
            # Update the assigned group
            ticket.assigned_group = qa_group
            messages.info(request, f'Ticket automatically assigned to {qa_group.name} group.')
    
    # Update status
    ticket.status = status
    ticket.save(update_fields=['status', 'assigned_group', 'updated_at'])
    
    messages.success(request, f'Ticket status changed to {status.name}.')
    return redirect('ticket-detail', pk=ticket.pk)

@login_required
def group_management(request):
    """View for managing user groups (for admins only)."""
    if not request.user.is_superuser:
        messages.error(request, "You don't have permission to access group management.")
        return redirect('dashboard')
    
    groups = Group.objects.all()
    
    context = {
        'groups': groups
    }
    
    return render(request, 'tickets/group_management.html', context)

@login_required
@staff_member_required
def create_group(request):
    """Create a new group."""
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            group, created = Group.objects.get_or_create(name=name)
            if created:
                messages.success(request, f'Group "{name}" created successfully.')
            else:
                messages.warning(request, f'Group "{name}" already exists.')
        else:
            messages.error(request, 'Group name is required.')
    return redirect('group-management')

@login_required
@staff_member_required
def delete_group(request, pk):
    """Delete an existing group."""
    group = get_object_or_404(Group, pk=pk)
    
    if request.method == 'POST':
        name = group.name
        
        # Unassign this group from all tickets
        tickets = Ticket.objects.filter(assigned_group=group)
        for ticket in tickets:
            # Record history
            TicketHistory.objects.create(
                ticket=ticket,
                changed_by=request.user,
                field_name='assigned_group',
                old_value=name,
                new_value='None'
            )
            
            # Update ticket
            ticket.assigned_group = None
            ticket.save(update_fields=['assigned_group', 'updated_at'])
        
        # Delete the group
        group.delete()
        messages.success(request, f'Group "{name}" deleted successfully.')
    
    return redirect('group-management')

@login_required
@staff_member_required
def group_members(request, pk):
    """Get members of a group."""
    group = get_object_or_404(Group, pk=pk)
    members = group.user_set.all()
    
    members_data = [
        {
            'id': member.id,
            'name': member.get_full_name() or member.username
        }
        for member in members
    ]
    
    return JsonResponse({'members': members_data})

@login_required
@staff_member_required
def add_group_member(request, pk):
    """Add a user to a group."""
    if request.method == 'POST':
        group = get_object_or_404(Group, pk=pk)
        
        try:
            data = json.loads(request.body)
            user_id = data.get('user_id')
            if not user_id:
                return JsonResponse({'success': False, 'error': 'User ID is required.'})
            
            # Debug info
            print(f"Adding user ID {user_id} to group {group.name} (ID: {pk})")
            
            # Get the user
            try:
                user = get_object_or_404(User, pk=user_id)
                
                # Check if user is already in the group
                if user.groups.filter(id=group.id).exists():
                    return JsonResponse({
                        'success': False, 
                        'error': f'User {user.username} is already a member of this group.'
                    })
                
                # Add user to group
                group.user_set.add(user)
                
                print(f"Successfully added user {user.username} to group {group.name}")
                
                return JsonResponse({
                    'success': True, 
                    'member': {
                        'id': user.id,
                        'name': user.get_full_name() or user.username
                    }
                })
            except User.DoesNotExist:
                return JsonResponse({'success': False, 'error': f'User with ID {user_id} not found.'})
                
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error adding group member: {str(e)}")
            return JsonResponse({'success': False, 'error': f'Invalid request data: {str(e)}'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method.'})

@login_required
@staff_member_required
def remove_group_member(request, pk, user_id):
    """Remove a user from a group."""
    if request.method == 'POST':
        group = get_object_or_404(Group, pk=pk)
        user = get_object_or_404(User, pk=user_id)
        
        # Unassign this user from tickets assigned to them through this group
        tickets = Ticket.objects.filter(assigned_group=group, assigned_to=user)
        for ticket in tickets:
            # Record history
            TicketHistory.objects.create(
                ticket=ticket,
                changed_by=request.user,
                field_name='assigned_to',
                old_value=user.get_full_name() or user.username,
                new_value='None'
            )
            
            # Update ticket
            ticket.assigned_to = None
            ticket.save(update_fields=['assigned_to', 'updated_at'])
        
        # Remove user from group
        group.user_set.remove(user)
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method.'})

@login_required
@staff_member_required
def group_tickets(request, pk):
    """Get tickets assigned to a group."""
    group = get_object_or_404(Group, pk=pk)
    tickets = Ticket.objects.filter(assigned_group=group)
    
    tickets_data = [
        {
            'id': ticket.id,
            'title': ticket.title,
            'status': ticket.status.name if ticket.status else 'None',
            'status_color': ticket.status.color if ticket.status else '#999',
            'priority': ticket.priority.name if ticket.priority else 'None',
            'priority_color': ticket.priority.color if ticket.priority else '#999',
            'created_at': ticket.created_at.strftime('%b %d, %Y')
        }
        for ticket in tickets
    ]
    
    return JsonResponse({'tickets': tickets_data})

@login_required
@staff_member_required
def available_users(request, group_id):
    """Get users available to add to a group."""
    group = get_object_or_404(Group, pk=group_id)
    
    # Get users not in the group
    users = User.objects.exclude(groups=group).filter(is_active=True)
    
    users_data = [
        {
            'id': user.id,
            'name': user.get_full_name() or user.username
        }
        for user in users
    ]
    
    # Add some debugging info
    print(f"Available users for group {group.name} (ID: {group_id}): {len(users_data)}")
    
    return JsonResponse({'users': users_data})

@login_required
def kanban_board(request):
    """Display a Kanban board view of tickets."""
    # Get all ticket statuses for columns
    statuses = TicketStatus.objects.all().order_by('order')
    
    # Get all ticket types, priorities, categories and requestors for the filter
    ticket_types = TicketType.objects.all()
    ticket_priorities = TicketPriority.objects.all()
    ticket_categories = TicketCategory.objects.all()
    ticket_requestors = TicketRequestor.objects.all()
    
    # Apply filters similar to ticket list view
    tickets = Ticket.objects.all()
    
    # Filter by search term
    search_term = request.GET.get('search', '')
    if search_term:
        tickets = tickets.filter(
            Q(title__icontains=search_term) | 
            Q(description__icontains=search_term) |
            Q(key_stakeholders__icontains=search_term)
        )
    
    # Filter by type
    type_id = request.GET.get('type', '')
    if type_id:
        tickets = tickets.filter(type__id=type_id)
    
    # Filter by priority
    priority_id = request.GET.get('priority', '')
    if priority_id:
        tickets = tickets.filter(priority__id=priority_id)
    
    # Filter by category
    category_id = request.GET.get('category', '')
    if category_id:
        tickets = tickets.filter(category__id=category_id)
    
    # Filter by requestor
    requestor_id = request.GET.get('requestor', '')
    if requestor_id:
        tickets = tickets.filter(requestor__id=requestor_id)
    
    # Serialize tickets and statuses for the React app
    tickets_data = []
    for ticket in tickets:
        ticket_data = {
            'id': ticket.id,
            'title': ticket.title,
            'status': {
                'id': ticket.status.id,
                'name': ticket.status.name,
                'color': ticket.status.color
            } if ticket.status else None,
            'priority': {
                'id': ticket.priority.id,
                'name': ticket.priority.name,
                'color': ticket.priority.color
            } if ticket.priority else None,
            'type': {
                'id': ticket.type.id,
                'name': ticket.type.name
            } if ticket.type else None,
            'category': {
                'id': ticket.category.id,
                'name': ticket.category.name
            } if ticket.category else None,
            'requestor': {
                'id': ticket.requestor.id,
                'name': ticket.requestor.name
            } if ticket.requestor else None,
            'assigned_to': {
                'id': ticket.assigned_to.id,
                'username': ticket.assigned_to.username
            } if ticket.assigned_to else None,
            'created_by': {
                'id': ticket.created_by.id,
                'username': ticket.created_by.username
            },
            'created_at': ticket.created_at.isoformat(),
            'updated_at': ticket.updated_at.isoformat()
        }
        tickets_data.append(ticket_data)
    
    statuses_data = []
    for status in statuses:
        status_data = {
            'id': status.id,
            'name': status.name,
            'color': status.color,
            'order': status.order
        }
        statuses_data.append(status_data)
    
    # JSON encode the data for passing to the template
    tickets_json = json.dumps(tickets_data)
    statuses_json = json.dumps(statuses_data)
    
    context = {
        'tickets_json': tickets_json,
        'statuses_json': statuses_json,
        'ticket_types': ticket_types,
        'ticket_priorities': ticket_priorities,
        'ticket_categories': ticket_categories,
        'ticket_requestors': ticket_requestors
    }
    
    return render(request, 'tickets/kanban_board.html', context) 