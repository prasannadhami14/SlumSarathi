from django.db import models
from django.core.validators import MinValueValidator, URLValidator
from django.utils.translation import gettext_lazy as _
from accounts.models import User
import uuid
from datetime import datetime
from django.urls import reverse

class EventCategory(models.Model):
    """Categories for organizing events"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)
    
    class Meta:
        verbose_name = _('event category')
        verbose_name_plural = _('event categories')
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Event(models.Model):
    """Model for events and workshops"""
    EVENT_TYPES = (
        ('online', 'Online Event'),
        ('onsite', 'Onsite Event'),
        ('hybrid', 'Hybrid Event'),
    )
    
    EVENT_STATUS = (
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organizer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='organized_events',
        limit_choices_to={'user_type': 2}  # Only organizers can create events
    )
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()
    event_type = models.CharField(max_length=10, choices=EVENT_TYPES)
    category = models.ForeignKey(
        EventCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='events'
    )
    
    # Event timing
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    registration_deadline = models.DateTimeField(null=True, blank=True)
    
    # Location details
    venue_name = models.CharField(max_length=200, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    online_link = models.URLField(blank=True, validators=[URLValidator()])
    
    # Event logistics
    capacity = models.PositiveIntegerField(null=True, blank=True)
    is_free = models.BooleanField(default=True)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )
    status = models.CharField(max_length=10, choices=EVENT_STATUS, default='draft')
    
    # Media
    featured_image = models.ImageField(upload_to='event_images/', blank=True, null=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    views = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = _('event')
        verbose_name_plural = _('events')
        ordering = ['-start_datetime']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['event_type']),
            models.Index(fields=['start_datetime']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.get_event_type_display()})"
    
    def get_absolute_url(self):
        return reverse('event_detail', kwargs={'slug': self.slug})
    
    def save(self, *args, **kwargs):
        """Ensure price consistency"""
        if self.is_free:
            self.price = None
        super().save(*args, **kwargs)
    
    @property
    def is_upcoming(self):
        """Check if event is in the future"""
        return self.start_datetime > datetime.now()
    
    @property
    def is_past(self):
        """Check if event has already happened"""
        return self.end_datetime < datetime.now()
    
    @property
    def registration_open(self):
        """Check if registration is still open"""
        if self.registration_deadline:
            return self.registration_deadline > datetime.now()
        return self.is_upcoming
    
    @property
    def available_seats(self):
        """Calculate available seats if capacity is set"""
        if self.capacity:
            return self.capacity - self.registrations.count()
        return None
    
    @property
    def location_display(self):
        """Display location based on event type"""
        if self.event_type == 'online':
            return "Online Event"
        location_parts = [self.venue_name, self.city, self.country]
        return ", ".join(filter(None, location_parts))

class EventImage(models.Model):
    """Additional images for events"""
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(upload_to='event_images/')
    caption = models.CharField(max_length=100, blank=True)
    is_featured = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = _('event image')
        verbose_name_plural = _('event images')
        ordering = ['order']
    
    def __str__(self):
        return f"Image for {self.event.title}"

class EventRegistration(models.Model):
    """Model for event registrations"""
    STATUS_CHOICES = (
        ('registered', 'Registered'),
        ('attended', 'Attended'),
        ('cancelled', 'Cancelled'),
        ('waitlisted', 'Waitlisted'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='registrations'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='event_registrations'
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='registered'
    )
    registration_date = models.DateTimeField(auto_now_add=True)
    attended = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    
    # Payment fields (for paid events)
    payment_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    payment_date = models.DateTimeField(null=True, blank=True)
    payment_method = models.CharField(max_length=50, blank=True)
    
    class Meta:
        verbose_name = _('event registration')
        verbose_name_plural = _('event registrations')
        unique_together = ('event', 'user')
        ordering = ['-registration_date']
    
    def __str__(self):
        return f"{self.user.email} registered for {self.event.title}"
    
    def save(self, *args, **kwargs):
        """Set payment amount for paid events"""
        if self.event.price and not self.payment_amount:
            self.payment_amount = self.event.price
        super().save(*args, **kwargs)

class EventAgenda(models.Model):
    """Detailed agenda for events"""
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='agenda_items'
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    speaker = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=100, blank=True)
    is_break = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = _('event agenda item')
        verbose_name_plural = _('event agenda items')
        ordering = ['order', 'start_time']
    
    def __str__(self):
        return f"{self.title} at {self.event.title}"

class EventFeedback(models.Model):
    """Feedback from event attendees"""
    RATING_CHOICES = [
        (1, '★☆☆☆☆ - Poor'),
        (2, '★★☆☆☆ - Fair'),
        (3, '★★★☆☆ - Good'),
        (4, '★★★★☆ - Very Good'),
        (5, '★★★★★ - Excellent'),
    ]
    
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='feedbacks'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='event_feedbacks'
    )
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    anonymous = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = _('event feedback')
        verbose_name_plural = _('event feedbacks')
        unique_together = ('event', 'user')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Feedback for {self.event.title} by {self.user.email}"
    
    @property
    def stars(self):
        return '★' * self.rating + '☆' * (5 - self.rating)