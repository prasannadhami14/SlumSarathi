# events/urls.py
from django.urls import path
from .views import (
    EventListView, EventDetailView, EventCreateView,
    EventUpdateView, EventDeleteView, register_for_event,EventRegistrationsView,promote_attendee,remove_registration
)
from django.views.defaults import permission_denied

app_name = 'events'

urlpatterns = [
    path('', EventListView.as_view(), name='event_list'),
    path('create/', EventCreateView.as_view(), name='event_create'),
    path('<slug:slug>/', EventDetailView.as_view(), name='event_detail'),
    path('<slug:slug>/edit/', EventUpdateView.as_view(), name='event_edit'),
    path('<slug:slug>/delete/', EventDeleteView.as_view(), name='event_delete'),
    path('<slug:slug>/register/', register_for_event, name='event_register'),
    path('403/', permission_denied, {'exception': Exception("Permission Denied")}),
    path('<slug:slug>/registrations/', EventRegistrationsView.as_view(), name='event_registrations'),
    path('registrations/<uuid:pk>/promote/', promote_attendee, name='promote_attendee'),
    path('registrations/<uuid:pk>/remove/', remove_registration, name='remove_registration')
]