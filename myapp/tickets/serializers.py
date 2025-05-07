from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from .models import (
    Ticket, TicketStatus, TicketPriority, TicketType,
    TicketComment, TicketAttachment, TicketHistory,
    TicketCategory, TicketRequestor
)

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """Serializer for user objects."""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class GroupSerializer(serializers.ModelSerializer):
    """Serializer for group objects."""
    
    class Meta:
        model = Group
        fields = ['id', 'name']

class TicketStatusSerializer(serializers.ModelSerializer):
    """Serializer for ticket status."""
    
    class Meta:
        model = TicketStatus
        fields = ['id', 'name', 'description', 'color', 'order']

class TicketPrioritySerializer(serializers.ModelSerializer):
    """Serializer for ticket priority."""
    
    class Meta:
        model = TicketPriority
        fields = ['id', 'name', 'description', 'color', 'order']

class TicketTypeSerializer(serializers.ModelSerializer):
    """Serializer for ticket type."""
    
    class Meta:
        model = TicketType
        fields = ['id', 'name', 'description']

class TicketCategorySerializer(serializers.ModelSerializer):
    """Serializer for ticket category."""
    
    class Meta:
        model = TicketCategory
        fields = ['id', 'name', 'description']

class TicketRequestorSerializer(serializers.ModelSerializer):
    """Serializer for ticket requestor."""
    
    class Meta:
        model = TicketRequestor
        fields = ['id', 'name', 'description']

class TicketCommentSerializer(serializers.ModelSerializer):
    """Serializer for ticket comments."""
    author = UserSerializer(read_only=True)
    
    class Meta:
        model = TicketComment
        fields = ['id', 'ticket', 'author', 'content', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class TicketAttachmentSerializer(serializers.ModelSerializer):
    """Serializer for ticket attachments."""
    uploaded_by = UserSerializer(read_only=True)
    
    class Meta:
        model = TicketAttachment
        fields = ['id', 'ticket', 'file', 'uploaded_by', 'uploaded_at', 'description']
        read_only_fields = ['uploaded_at']

class TicketHistorySerializer(serializers.ModelSerializer):
    """Serializer for ticket history."""
    changed_by = UserSerializer(read_only=True)
    
    class Meta:
        model = TicketHistory
        fields = ['id', 'ticket', 'changed_by', 'changed_at', 'field_name', 'old_value', 'new_value']
        read_only_fields = ['changed_at']

class TicketSerializer(serializers.ModelSerializer):
    """Serializer for tickets."""
    created_by = UserSerializer(read_only=True)
    assigned_to = UserSerializer(required=False, allow_null=True)
    assigned_group = GroupSerializer(required=False, allow_null=True)
    status = TicketStatusSerializer(required=False, allow_null=True)
    priority = TicketPrioritySerializer(required=False, allow_null=True)
    type = TicketTypeSerializer(required=False, allow_null=True)
    category = TicketCategorySerializer(required=False, allow_null=True)
    requestor = TicketRequestorSerializer(required=False, allow_null=True)
    comments = TicketCommentSerializer(many=True, read_only=True)
    attachments = TicketAttachmentSerializer(many=True, read_only=True)
    history = TicketHistorySerializer(many=True, read_only=True)
    
    class Meta:
        model = Ticket
        fields = [
            'id', 'title', 'description', 'created_by', 'assigned_to', 
            'assigned_group', 'status', 'priority', 'type', 'category', 'requestor',
            'key_stakeholders', 'created_at', 'updated_at', 'due_date', 
            'comments', 'attachments', 'history'
        ]
        read_only_fields = ['created_at', 'updated_at']

class TicketListSerializer(serializers.ModelSerializer):
    """Simplified serializer for ticket list views."""
    created_by = serializers.StringRelatedField()
    assigned_to = serializers.StringRelatedField()
    assigned_group = serializers.StringRelatedField()
    status = serializers.StringRelatedField()
    priority = serializers.StringRelatedField()
    type = serializers.StringRelatedField()
    category = serializers.StringRelatedField()
    requestor = serializers.StringRelatedField()
    
    class Meta:
        model = Ticket
        fields = [
            'id', 'title', 'created_by', 'assigned_to', 'assigned_group',
            'status', 'priority', 'type', 'category', 'requestor',
            'created_at', 'updated_at', 'due_date'
        ]
        read_only_fields = ['created_at', 'updated_at'] 