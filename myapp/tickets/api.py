from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from .models import (
    Ticket, TicketStatus, TicketPriority, TicketType,
    TicketComment, TicketAttachment, TicketHistory
)
from .serializers import (
    UserSerializer, GroupSerializer,
    TicketSerializer, TicketListSerializer,
    TicketStatusSerializer, TicketPrioritySerializer, TicketTypeSerializer,
    TicketCommentSerializer, TicketAttachmentSerializer, TicketHistorySerializer
)

User = get_user_model()

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # Write permissions are only allowed to the owner
        return obj.created_by == request.user

class IsAssignedOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow assigned users to edit tickets.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # Check if user is assigned to the ticket or is in the assigned group
        return (request.user.is_superuser or
                obj.created_by == request.user or
                obj.assigned_to == request.user or
                (obj.assigned_group and obj.assigned_group in request.user.groups.all()))

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for viewing users."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name']

class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for viewing groups."""
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

class TicketStatusViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for viewing ticket statuses."""
    queryset = TicketStatus.objects.all().order_by('order')
    serializer_class = TicketStatusSerializer
    permission_classes = [permissions.IsAuthenticated]

class TicketPriorityViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for viewing ticket priorities."""
    queryset = TicketPriority.objects.all().order_by('order')
    serializer_class = TicketPrioritySerializer
    permission_classes = [permissions.IsAuthenticated]

class TicketTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for viewing ticket types."""
    queryset = TicketType.objects.all()
    serializer_class = TicketTypeSerializer
    permission_classes = [permissions.IsAuthenticated]

class TicketViewSet(viewsets.ModelViewSet):
    """API endpoint for managing tickets."""
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated, IsAssignedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'updated_at', 'due_date', 'status__order', 'priority__order']
    ordering = ['-updated_at']
    
    def get_serializer_class(self):
        """Return different serializers for list vs detail."""
        if self.action == 'list':
            return TicketListSerializer
        return TicketSerializer
    
    def get_queryset(self):
        """Filter tickets based on user permissions."""
        user = self.request.user
        queryset = Ticket.objects.all()
        
        # Apply query param filters
        status = self.request.query_params.get('status', None)
        if status:
            queryset = queryset.filter(status__name=status)
            
        priority = self.request.query_params.get('priority', None)
        if priority:
            queryset = queryset.filter(priority__name=priority)
            
        ticket_type = self.request.query_params.get('type', None)
        if ticket_type:
            queryset = queryset.filter(type__name=ticket_type)
            
        assigned_to = self.request.query_params.get('assigned_to', None)
        if assigned_to == 'me':
            queryset = queryset.filter(assigned_to=user)
        elif assigned_to:
            queryset = queryset.filter(assigned_to__username=assigned_to)
            
        created_by = self.request.query_params.get('created_by', None)
        if created_by == 'me':
            queryset = queryset.filter(created_by=user)
        elif created_by:
            queryset = queryset.filter(created_by__username=created_by)
            
        assigned_group = self.request.query_params.get('assigned_group', None)
        if assigned_group == 'my':
            queryset = queryset.filter(assigned_group__in=user.groups.all())
        elif assigned_group:
            queryset = queryset.filter(assigned_group__name=assigned_group)
        
        # If user is not superuser, limit visible tickets
        if not user.is_superuser:
            user_groups = user.groups.all()
            queryset = queryset.filter(
                Q(created_by=user) |
                Q(assigned_to=user) |
                Q(assigned_group__in=user_groups)
            ).distinct()
        
        return queryset
    
    def perform_create(self, serializer):
        """Set the created_by field to the current user."""
        serializer.save(created_by=self.request.user)
    
    @action(detail=True)
    def comments(self, request, pk=None):
        """Return the comments for a ticket."""
        ticket = self.get_object()
        comments = ticket.comments.all()
        page = self.paginate_queryset(comments)
        if page is not None:
            serializer = TicketCommentSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = TicketCommentSerializer(comments, many=True)
        return Response(serializer.data)
    
    @action(detail=True)
    def attachments(self, request, pk=None):
        """Return the attachments for a ticket."""
        ticket = self.get_object()
        attachments = ticket.attachments.all()
        page = self.paginate_queryset(attachments)
        if page is not None:
            serializer = TicketAttachmentSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = TicketAttachmentSerializer(attachments, many=True)
        return Response(serializer.data)
    
    @action(detail=True)
    def history(self, request, pk=None):
        """Return the history for a ticket."""
        ticket = self.get_object()
        history = ticket.history.all()
        page = self.paginate_queryset(history)
        if page is not None:
            serializer = TicketHistorySerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = TicketHistorySerializer(history, many=True)
        return Response(serializer.data)

class TicketCommentViewSet(viewsets.ModelViewSet):
    """API endpoint for managing ticket comments."""
    queryset = TicketComment.objects.all()
    serializer_class = TicketCommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    
    def get_queryset(self):
        """Filter comments to those the user has access to."""
        user = self.request.user
        
        # If filtering by ticket
        ticket_id = self.request.query_params.get('ticket', None)
        if ticket_id:
            queryset = TicketComment.objects.filter(ticket_id=ticket_id)
        else:
            queryset = TicketComment.objects.all()
        
        # If user is not superuser, limit visible comments
        if not user.is_superuser:
            user_groups = user.groups.all()
            queryset = queryset.filter(
                Q(ticket__created_by=user) |
                Q(ticket__assigned_to=user) |
                Q(ticket__assigned_group__in=user_groups)
            ).distinct()
        
        return queryset
    
    def perform_create(self, serializer):
        """Set the author field to the current user."""
        serializer.save(author=self.request.user)

class TicketAttachmentViewSet(viewsets.ModelViewSet):
    """API endpoint for managing ticket attachments."""
    queryset = TicketAttachment.objects.all()
    serializer_class = TicketAttachmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    
    def get_queryset(self):
        """Filter attachments to those the user has access to."""
        user = self.request.user
        
        # If filtering by ticket
        ticket_id = self.request.query_params.get('ticket', None)
        if ticket_id:
            queryset = TicketAttachment.objects.filter(ticket_id=ticket_id)
        else:
            queryset = TicketAttachment.objects.all()
        
        # If user is not superuser, limit visible attachments
        if not user.is_superuser:
            user_groups = user.groups.all()
            queryset = queryset.filter(
                Q(ticket__created_by=user) |
                Q(ticket__assigned_to=user) |
                Q(ticket__assigned_group__in=user_groups)
            ).distinct()
        
        return queryset
    
    def perform_create(self, serializer):
        """Set the uploaded_by field to the current user."""
        serializer.save(uploaded_by=self.request.user)

class TicketHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for viewing ticket history."""
    queryset = TicketHistory.objects.all()
    serializer_class = TicketHistorySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter history to those the user has access to."""
        user = self.request.user
        
        # If filtering by ticket
        ticket_id = self.request.query_params.get('ticket', None)
        if ticket_id:
            queryset = TicketHistory.objects.filter(ticket_id=ticket_id)
        else:
            queryset = TicketHistory.objects.all()
        
        # If user is not superuser, limit visible history
        if not user.is_superuser:
            user_groups = user.groups.all()
            queryset = queryset.filter(
                Q(ticket__created_by=user) |
                Q(ticket__assigned_to=user) |
                Q(ticket__assigned_group__in=user_groups)
            ).distinct()
        
        return queryset 