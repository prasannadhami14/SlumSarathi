# events/views.py
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Event, EventRegistration
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.http import HttpResponseForbidden
from . import models
from .forms import EventForm

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
        return super().form_valid(form)

class EventUpdateView(LoginRequiredMixin, OrganizerRequiredMixin, UpdateView):
    model = Event
    template_name = 'events/event_form.html'
    fields = [
        'title', 'slug', 'description', 'event_type', 'category',
        'start_datetime', 'end_datetime', 'registration_deadline',
        'venue_name', 'address', 'city', 'state', 'country', 'online_link',
        'capacity', 'is_free', 'price', 'featured_image'
    ]

class EventDeleteView(LoginRequiredMixin, OrganizerRequiredMixin, DeleteView):
    model = Event
    template_name = 'events/event_confirm_delete.html'
    success_url = reverse_lazy('event_list')

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