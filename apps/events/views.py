# events/views.py
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy,reverse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Event, EventRegistration
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.http import HttpResponseForbidden
from . import models
from .forms import EventForm
from django.core.exceptions import PermissionDenied
from django.http import Http404

class EventListView(ListView):
    model = Event
    template_name = 'events/event_list.html'
    context_object_name = 'events'
    paginate_by = 10
    
    def get_queryset(self):
        # Base queryset - only published events
        queryset = Event.objects.all()
        
        # Optional: Add status filter if a specific status is requested
        status = self.request.GET.get('status')
        if status in ['draft', 'published', 'cancelled', 'completed']:
            queryset = queryset.filter(status=status)
        
        # Filter by event type if provided
        event_type = self.request.GET.get('type')
        if event_type in ['online', 'onsite', 'hybrid']:
            queryset = queryset.filter(event_type=event_type)
            
        # Filter by location if provided
        location = self.request.GET.get('location')
        if location:
            queryset = queryset.filter(
                Q(city__icontains=location) |
                Q(country__icontains=location)
            )
        
        # Order by start datetime (newest first)
        return queryset.order_by('-start_datetime')

class EventDetailView(DetailView):
    model = Event
    template_name = 'events/event_detail.html'
    context_object_name = 'event'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        queryset = super().get_queryset()
        # Allow preview for organizers and staff
        if self.request.user.is_staff or (self.request.user.is_authenticated and 
           queryset.filter(organizer=self.request.user).exists()):
            return queryset
        return queryset.filter(status='published')

    def get_object(self, queryset=None):
        try:
            return super().get_object(queryset)
        except Http404:
            slug = self.kwargs.get(self.slug_url_kwarg)
            if Event.objects.filter(slug=slug).exists():
                if self.request.user.is_authenticated:
                    raise PermissionDenied("You don't have permission to view this unpublished event")
                raise Http404("Event not found")  # Generic message for non-authenticated users
            raise Http404(f"No event found with slug: '{slug}'")

class OrganizerRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        event = self.get_object()
        return self.request.user == event.organizer

class EventCreateView(LoginRequiredMixin, CreateView):
    model = Event
    template_name = 'events/event_form.html'
    form_class = EventForm

    def form_valid(self, form):
        form.instance.organizer = self.request.user
        response = super().form_valid(form)
        if not self.object.slug:
            self.object.save()  # This will generate the slug
        return response
    def get_success_url(self):
        return reverse('events:event_detail', kwargs={'slug': self.object.slug})

class EventUpdateView(LoginRequiredMixin, OrganizerRequiredMixin, UpdateView):
    model = Event
    template_name = 'events/event_form.html'
    fields = [
        'title', 'description', 'event_type',
        'start_datetime', 'end_datetime', 'registration_deadline',
        'venue_name', 'address', 'city', 'state', 'country', 'online_link',
        'capacity', 'is_free', 'price', 'featured_image'
    ]
        
    def get_success_url(self):
        return reverse('events:event_detail', kwargs={'slug': self.object.slug})

class EventDeleteView(LoginRequiredMixin, OrganizerRequiredMixin, DeleteView):
    model = Event
    template_name = 'events/event_confirm_delete.html'
    success_url = reverse_lazy('events:event_list')

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.http import HttpResponseForbidden
from .models import Event, EventRegistration

@login_required
def register_for_event(request, slug):
    # Get the event or return 404
    event = get_object_or_404(Event, slug=slug)
    
    # Check if event is published
    if event.status != 'published':
        messages.error(request, "This event is not available for registration")
        return redirect('events:event_detail', slug=slug)
    
    # Check if registration is open
    if not event.registration_open:
        messages.error(request, "Registration is closed for this event")
        return redirect('events:event_detail', slug=slug)
    
    # Check if event is in the past
    if event.is_past:
        messages.error(request, "This event has already occurred")
        return redirect('events:event_detail', slug=slug)
    
    # Check capacity
    if event.capacity and event.registrations.count() >= event.capacity:
        messages.error(request, "This event has reached capacity")
        return redirect('events:event_detail', slug=slug)
    
    # Check if already registered
    if EventRegistration.objects.filter(event=event, user=request.user).exists():
        messages.warning(request, "You are already registered for this event")
        return redirect('events:event_detail', slug=slug)
    
    # Register the user
    registration = EventRegistration.objects.create(
        event=event,
        user=request.user,
        status='waitlisted' if event.capacity and 
              event.available_seats <= 0 else 'registered'
    )
    
    messages.success(request, "Successfully registered for the event")
    return redirect('events:event_detail', slug=slug)
class EventRegistrationsView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    template_name = 'events/event_registrations.html'
    context_object_name = 'registrations'
    
    def test_func(self):
        event = get_object_or_404(Event, slug=self.kwargs['slug'])
        return self.request.user == event.organizer or self.request.user.is_staff
    
    def get_queryset(self):
        event = get_object_or_404(Event, slug=self.kwargs['slug'])
        return EventRegistration.objects.filter(event=event).select_related('user')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['event'] = get_object_or_404(Event, slug=self.kwargs['slug'])
        return context
@login_required
def promote_attendee(request, pk):
    registration = get_object_or_404(EventRegistration, pk=pk)
    if not (request.user == registration.event.organizer or request.user.is_staff):
        raise PermissionDenied
    
    if registration.event.available_seats > 0 and registration.status == 'waitlisted':
        registration.status = 'registered'
        registration.save()
        messages.success(request, f"{registration.user.get_full_name()} promoted to registered attendee")
    else:
        messages.error(request, "No available seats or attendee not waitlisted")
    
    return redirect('events:event_registrations', slug=registration.event.slug)

@login_required
def remove_registration(request, pk):
    registration = get_object_or_404(EventRegistration, pk=pk)
    if not (request.user == registration.event.organizer or request.user.is_staff):
        raise PermissionDenied
    
    user_name = registration.user.get_full_name()
    registration.delete()
    messages.success(request, f"Registration for {user_name} removed successfully")
    
    return redirect('events:event_registrations', slug=registration.event.slug)