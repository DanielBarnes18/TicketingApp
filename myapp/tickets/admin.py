from django.contrib import admin
from .models import (
    Ticket, TicketStatus, TicketPriority, TicketType,
    TicketAttachment, TicketComment, TicketHistory,
    TicketCategory, TicketRequestor
)

class TicketAttachmentInline(admin.TabularInline):
    model = TicketAttachment
    extra = 0

class TicketCommentInline(admin.TabularInline):
    model = TicketComment
    extra = 0
    readonly_fields = ('created_at', 'updated_at')

class TicketHistoryInline(admin.TabularInline):
    model = TicketHistory
    extra = 0
    readonly_fields = ('changed_by', 'changed_at', 'field_name', 'old_value', 'new_value')
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'priority', 'type', 'category', 'requestor', 'created_by', 'assigned_to', 'assigned_group', 'created_at', 'updated_at', 'is_overdue_display')
    list_filter = ('status', 'priority', 'type', 'category', 'requestor', 'created_at', 'updated_at', 'due_date')
    search_fields = ('title', 'description', 'key_stakeholders', 'created_by__username', 'assigned_to__username')
    date_hierarchy = 'created_at'
    inlines = [TicketAttachmentInline, TicketCommentInline, TicketHistoryInline]
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'created_by')
        }),
        ('Assignment', {
            'fields': ('assigned_to', 'assigned_group')
        }),
        ('Classification', {
            'fields': ('status', 'priority', 'type', 'category', 'requestor')
        }),
        ('Additional Information', {
            'fields': ('key_stakeholders',)
        }),
        ('Dates', {
            'fields': ('due_date',)
        }),
    )
    
    @admin.display(
        boolean=True,
        description="Overdue"
    )
    def is_overdue_display(self, obj):
        return obj.is_overdue

@admin.register(TicketStatus)
class TicketStatusAdmin(admin.ModelAdmin):
    list_display = ('name', 'order', 'color', 'description')
    search_fields = ('name', 'description')
    ordering = ('order',)

@admin.register(TicketPriority)
class TicketPriorityAdmin(admin.ModelAdmin):
    list_display = ('name', 'order', 'color', 'description')
    search_fields = ('name', 'description')
    ordering = ('order',)

@admin.register(TicketType)
class TicketTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name', 'description')

@admin.register(TicketCategory)
class TicketCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name', 'description')

@admin.register(TicketRequestor)
class TicketRequestorAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name', 'description')

@admin.register(TicketComment)
class TicketCommentAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'author', 'created_at', 'updated_at')
    list_filter = ('created_at', 'author')
    search_fields = ('content', 'ticket__title', 'author__username')
    date_hierarchy = 'created_at'
    
@admin.register(TicketAttachment)
class TicketAttachmentAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'uploaded_by', 'uploaded_at', 'description')
    list_filter = ('uploaded_at', 'uploaded_by')
    search_fields = ('description', 'ticket__title', 'uploaded_by__username')
    date_hierarchy = 'uploaded_at'

@admin.register(TicketHistory)
class TicketHistoryAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'field_name', 'old_value', 'new_value', 'changed_by', 'changed_at')
    list_filter = ('changed_at', 'field_name', 'changed_by')
    search_fields = ('ticket__title', 'field_name', 'old_value', 'new_value', 'changed_by__username')
    date_hierarchy = 'changed_at'
    readonly_fields = ('changed_by', 'changed_at', 'field_name', 'old_value', 'new_value')
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False 