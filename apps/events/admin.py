from django.contrib import admin
from .models import (
    Event, EventCategory, EventImage, EventRegistration, EventAgenda, EventFeedback
)

@admin.register(EventCategory)
class EventCategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = ("name", "slug")
    search_fields = ("name",)

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    list_display = ("title", "event_type", "category", "start_datetime", "status")
    list_filter = ("event_type", "category", "status")
    search_fields = ("title", "description", "city", "country")
    readonly_fields = ("views", "created_at", "updated_at")
    date_hierarchy = "start_datetime"
    ordering = ("-start_datetime",)
    filter_horizontal = ()
    fieldsets = (
        (None, {
            "fields": ("title", "slug", "organizer", "description", "event_type", "category", "status")
        }),
        ("Timing", {
            "fields": ("start_datetime", "end_datetime", "registration_deadline")
        }),
        ("Location", {
            "fields": ("venue_name", "address", "city", "state", "country", "online_link")
        }),
        ("Logistics", {
            "fields": ("capacity", "is_free", "price")
        }),
        ("Media", {
            "fields": ("featured_image",)
        }),
        ("Meta", {
            "fields": ("views", "created_at", "updated_at")
        }),
    )

@admin.register(EventImage)
class EventImageAdmin(admin.ModelAdmin):
    list_display = ("event", "caption", "is_featured", "order")
    list_filter = ("event", "is_featured")
    ordering = ("event", "order")

@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ("event", "user", "status", "registration_date", "attended")
    list_filter = ("status", "attended", "event")
    search_fields = ("user__email", "event__title")

@admin.register(EventAgenda)
class EventAgendaAdmin(admin.ModelAdmin):
    list_display = ("event", "title", "start_time", "end_time", "speaker", "is_break", "order")
    list_filter = ("event", "is_break")
    ordering = ("event", "order", "start_time")

@admin.register(EventFeedback)
class EventFeedbackAdmin(admin.ModelAdmin):
    list_display = ("event", "user", "rating", "anonymous", "created_at")
    list_filter = ("rating", "anonymous", "event")
    search_fields = ("user__email", "event__title", "comment")
    ordering = ("-created_at",)