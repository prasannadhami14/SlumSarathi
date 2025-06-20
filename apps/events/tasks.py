from celery import shared_task
from django.http import HttpRequest
from .utils import send_event_published_email
from .models import Event, EventRegistration

@shared_task
def test_celery():
    print("Test Celery task executed!")
    return "It works!"
@shared_task
def send_event_published_email_task(event_id, user_ids, domain):
    """
    Celery task to send email notifications for a published event.
    Args:
        event_id: UUID of the Event instance
        user_ids: List of user UUIDs to notify
        domain: Domain for URL building (e.g., 'localhost:8000')
    """
    print(f"Celery task started for event {event_id} with users {user_ids} and domain {domain}")

    try:
        event = Event.objects.get(id=event_id)
        registrations = EventRegistration.objects.filter(event=event, user__id__in=user_ids)
        users = [reg.user for reg in registrations if reg.user.email]

        if users:
            # Create a dummy request for URL building
            request = HttpRequest()
            request.META['HTTP_HOST'] = domain
            request.META['SERVER_PROTOCOL'] = 'http'  # Adjust to 'https' in production

            # Send emails
            sent_count, invalid_emails = send_event_published_email(event, users, request)

            # Log results
            if invalid_emails:
                from django.contrib import messages
                messages.warning(
                    request,
                    f"Failed to send emails to {len(invalid_emails)} invalid addresses: {', '.join(invalid_emails)}"
                )
            if sent_count:
                messages.success(
                    request,
                    f"Sent notification emails to {sent_count} registered users for event '{event.title}'"
                )
    except Event.DoesNotExist:
        pass  # Log or handle if needed