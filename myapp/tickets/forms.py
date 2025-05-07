from django import forms
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from .models import (
    Ticket, TicketStatus, TicketPriority, TicketType,
    TicketAttachment, TicketComment, TicketCategory, TicketRequestor
)

User = get_user_model()

class TicketForm(forms.ModelForm):
    """Form for creating and editing tickets."""
    
    class Meta:
        model = Ticket
        fields = [
            'title', 'description', 'assigned_to', 'assigned_group',
            'status', 'priority', 'type', 'category', 'requestor', 'key_stakeholders', 'due_date'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'key_stakeholders': forms.Textarea(attrs={'rows': 3}),
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Add Bootstrap classes
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            
        # Set initial status if creating new ticket
        if not self.instance.pk and TicketStatus.objects.exists():
            # Default to first status (typically "Open" or "New")
            self.fields['status'].initial = TicketStatus.objects.order_by('order').first()
        # If editing an existing ticket, remove 'New' status from options
        elif self.instance.pk:
            new_status = TicketStatus.objects.filter(name='New').first()
            if new_status:
                # Remove 'New' status from choices
                self.fields['status'].queryset = TicketStatus.objects.exclude(id=new_status.id)
        
        # Limit assigned_to choices to active users
        self.fields['assigned_to'].queryset = User.objects.filter(is_active=True)
        
        # Removed the restriction for assigned_group
        # Now all available groups are shown for all users

class TicketCommentForm(forms.ModelForm):
    """Form for adding comments to a ticket."""
    
    class Meta:
        model = TicketComment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Add a comment...'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes
        self.fields['content'].widget.attrs['class'] = 'form-control'

class TicketAttachmentForm(forms.ModelForm):
    """Form for adding file attachments to a ticket."""
    
    class Meta:
        model = TicketAttachment
        fields = ['file', 'description']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes
        self.fields['file'].widget.attrs['class'] = 'form-control'
        self.fields['description'].widget.attrs['class'] = 'form-control'
        self.fields['description'].widget.attrs['placeholder'] = 'Brief description of the attachment'

class TicketFilterForm(forms.Form):
    """Form for filtering tickets on list view."""
    status = forms.ModelMultipleChoiceField(
        queryset=TicketStatus.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )
    priority = forms.ModelMultipleChoiceField(
        queryset=TicketPriority.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )
    type = forms.ModelMultipleChoiceField(
        queryset=TicketType.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )
    category = forms.ModelMultipleChoiceField(
        queryset=TicketCategory.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )
    requestor = forms.ModelMultipleChoiceField(
        queryset=TicketRequestor.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )
    assigned_group = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )
    assigned_to_me = forms.BooleanField(required=False)
    created_by_me = forms.BooleanField(required=False)
    user_comments = forms.BooleanField(required=False)
    search = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Search...'}))
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Add Bootstrap classes
        for field_name, field in self.fields.items():
            if field_name not in ['status', 'priority', 'type', 'category', 'requestor', 'assigned_group', 
                                 'assigned_to_me', 'created_by_me', 'user_comments']:
                field.widget.attrs['class'] = 'form-control'
        
        # Removed the restriction for assigned_group choices
        # Now all groups are shown in the dropdown for all users 