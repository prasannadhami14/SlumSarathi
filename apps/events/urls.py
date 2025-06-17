# events/urls.py
from django.urls import path
from .views import EventListView, EventDetailView, register_for_event

urlpatterns = [
    path('', EventListView.as_view(), name='event_list'),
    path('<slug:slug>/', EventDetailView.as_view(), name='event_detail'),
    path('<slug:slug>/register/', register_for_event, name='event_register'),
]