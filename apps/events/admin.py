from django.contrib import admin
from .models import (
    EventCategory,
    Event,
    EventImage,
    EventRegistration,
    EventAgenda,
    EventFeedback
)

class EventImageInline(admin.TabularInline):
    model = EventImage
    extra = 1

class EventAgendaInline(admin.TabularInline):
    model = EventAgenda
    extra = 1

class EventRegistrationInline(admin.TabularInline):
    model = EventRegistration
    extra = 0
    readonly_fields = ('user', 'registration_date', 'payment_amount')
    can_delete = False

class EventFeedbackInline(admin.TabularInline):
    model = EventFeedback
    extra = 0
    readonly_fields = ('user', 'rating', 'created_at')

class EventAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'organizer',
        'event_type',
        'start_datetime',
        'status',
        'registration_open',
        'available_seats'
    )
    list_filter = (
        'event_type',
        'status',
        'category',
        'is_free',
        'start_datetime'
    )
    search_fields = (
        'title',
        'description',
        'organizer__email',
        'venue_name',
        'city'
    )
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = (
        'views',
        'created_at',
        'updated_at',
        'available_seats'
    )
    inlines = [
        EventImageInline,
        EventAgendaInline,
        EventRegistrationInline,
        EventFeedbackInline
    ]
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'title',
                'slug',
                'organizer',
                'description',
                'category',
                'event_type',
                'status'
            )
        }),
        ('Date & Time', {
            'fields': (
                'start_datetime',
                'end_datetime',
                'registration_deadline'
            )
        }),
        ('Location', {
            'fields': (
                'venue_name',
                'address',
                'city',
                'state',
                'country',
                'online_link'
            )
        }),
        ('Logistics', {
            'fields': (
                'capacity',
                'is_free',
                'price',
                'featured_image'
            )
        }),
        ('Statistics', {
            'fields': (
                'views',
                'created_at',
                'updated_at'
            )
        })
    )
    actions = [
        'publish_events',
        'cancel_events',
        'mark_as_completed'
    ]

    def publish_events(self, request, queryset):
        queryset.update(status='published')
    publish_events.short_description = "Publish selected events"

    def cancel_events(self, request, queryset):
        queryset.update(status='cancelled')
    cancel_events.short_description = "Cancel selected events"

    def mark_as_completed(self, request, queryset):
        queryset.update(status='completed')
    mark_as_completed.short_description = "Mark selected events as completed"

admin.site.register(EventCategory)
admin.site.register(Event, EventAdmin)
admin.site.register(EventRegistration)
admin.site.register(EventFeedback)