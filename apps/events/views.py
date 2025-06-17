# events/views.py
from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404, redirect
from .models import Event, EventRegistration
from django.contrib import messages
from . import models
from django.http import HttpResponseForbidden

class EventListView(ListView):
    model = Event
    template_name = 'events/list.html'
    context_object_name = 'events'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = super().get_queryset().filter(status='published')
        
        # Filter by event type
        event_type = self.request.GET.get('type')
        if event_type in ['online', 'onsite', 'hybrid']:
            queryset = queryset.filter(event_type=event_type)
            
        # Filter by location
        location = self.request.GET.get('location')
        if location:
            queryset = queryset.filter(
                models.Q(city__icontains=location) |
                models.Q(country__icontains=location)
            )
        return queryset.order_by('start_datetime')

class EventDetailView(DetailView):
    model = Event
    template_name = 'events/detail.html'
    context_object_name = 'event'
    
    def get_queryset(self):
        return super().get_queryset().filter(status='published')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_registered'] = False
        if self.request.user.is_authenticated:
            context['is_registered'] = self.object.registrations.filter(
                user=self.request.user
            ).exists()
        return context

def register_for_event(request, slug):
    event = get_object_or_404(Event, slug=slug, status='published')
    
    if not event.registration_open:
        return HttpResponseForbidden("Registration is closed for this event")
    
    if event.capacity and event.registrations.count() >= event.capacity:
        return HttpResponseForbidden("This event has reached capacity")
    
    if EventRegistration.objects.filter(event=event, user=request.user).exists():
        messages.warning(request, "You are already registered for this event")
    else:
        EventRegistration.objects.create(
            event=event,
            user=request.user,
            status='waitlisted' if event.capacity and 
                  event.registrations.count() >= event.capacity else 'registered'
        )
        messages.success(request, "Successfully registered for the event")
    
    return redirect('event_detail', slug=slug)