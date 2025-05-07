from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import (
    UserViewSet, GroupViewSet,
    TicketViewSet, TicketStatusViewSet, TicketPriorityViewSet, TicketTypeViewSet,
    TicketCommentViewSet, TicketAttachmentViewSet, TicketHistoryViewSet
)

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'groups', GroupViewSet)
router.register(r'tickets', TicketViewSet)
router.register(r'statuses', TicketStatusViewSet)
router.register(r'priorities', TicketPriorityViewSet)
router.register(r'types', TicketTypeViewSet)
router.register(r'comments', TicketCommentViewSet)
router.register(r'attachments', TicketAttachmentViewSet)
router.register(r'history', TicketHistoryViewSet)

urlpatterns = [
    path('', include(router.urls)),
] 