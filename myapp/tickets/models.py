from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse
from django.utils import timezone

User = get_user_model()

class TicketStatus(models.Model):
    """Model representing ticket status (e.g., New, In Progress, QA, Resolved)."""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=20, help_text="Color code for UI display (e.g., #FF0000)")
    order = models.PositiveIntegerField(default=0, help_text="Display order in lists")
    
    class Meta:
        ordering = ['order']
        verbose_name_plural = 'Ticket statuses'
    
    def __str__(self):
        return self.name

class TicketPriority(models.Model):
    """Model representing ticket priority (e.g., Low, Medium, High, Critical)."""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=20, help_text="Color code for UI display (e.g., #FF0000)")
    order = models.PositiveIntegerField(default=0, help_text="Display order in lists")
    
    class Meta:
        ordering = ['order']
        verbose_name_plural = 'Ticket priorities'
    
    def __str__(self):
        return self.name

class TicketType(models.Model):
    """Model representing ticket type (e.g., Bug, Feature, Support)."""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

class TicketCategory(models.Model):
    """Model representing ticket category."""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = 'Ticket categories'
    
    def __str__(self):
        return self.name

class TicketRequestor(models.Model):
    """Model representing ticket requestor."""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = 'Ticket requestors'
    
    def __str__(self):
        return self.name

class Ticket(models.Model):
    """Main ticket model."""
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tickets')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tickets')
    assigned_group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tickets')
    status = models.ForeignKey(TicketStatus, on_delete=models.SET_NULL, null=True, related_name='tickets')
    priority = models.ForeignKey(TicketPriority, on_delete=models.SET_NULL, null=True, related_name='tickets')
    type = models.ForeignKey(TicketType, on_delete=models.SET_NULL, null=True, related_name='tickets')
    category = models.ForeignKey(TicketCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='tickets')
    requestor = models.ForeignKey(TicketRequestor, on_delete=models.SET_NULL, null=True, blank=True, related_name='tickets')
    key_stakeholders = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    due_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('ticket-detail', args=[str(self.id)])
    
    @property
    def is_overdue(self):
        if self.due_date and timezone.now() > self.due_date:
            return True
        return False

class TicketAttachment(models.Model):
    """Model for ticket attachments."""
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='ticket_attachments/')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=255, blank=True)
    
    def __str__(self):
        return f"Attachment for {self.ticket.title}"

class TicketComment(models.Model):
    """Model for comments on tickets."""
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment by {self.author.username} on {self.ticket.title}"

class TicketHistory(models.Model):
    """Model to track changes to tickets."""
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='history')
    changed_by = models.ForeignKey(User, on_delete=models.CASCADE)
    changed_at = models.DateTimeField(auto_now_add=True)
    field_name = models.CharField(max_length=100)
    old_value = models.TextField(blank=True, null=True)
    new_value = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-changed_at']
        verbose_name_plural = 'Ticket histories'
    
    def __str__(self):
        return f"{self.field_name} changed on {self.ticket.title}" 