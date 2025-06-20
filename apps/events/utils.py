from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError
import logging

# Set up logging
logger = logging.getLogger(__name__)

def send_event_published_email(event, users, request):
    """
    Send email notification to users when an event is published.
    Args:
        event: Event instance
        users: List of User instances to notify
        request: HttpRequest object for building absolute URLs
    Returns:
        tuple: (number of emails sent, list of invalid emails)
    """
    validator = EmailValidator()
    invalid_emails = []
    sent_count = 0

    # Get the current site domain
    domain = get_current_site(request).domain

    # Render email template
    subject = f"Event Published: {event.title}"

    for user in users:
        # Validate email address
        try:
            validator(user.email)
        except ValidationError:
            invalid_emails.append(user.email)
            logger.error(f"Invalid email address for user {user.username}: {user.email}")
            continue

        # Prepare context for email template
        context = {
            'user': user,
            'event': event,
            'domain': f"http://{domain}" if not request.is_secure() else f"https://{domain}",
        }

        # Render HTML content
        html_content = render_to_string('events/event_published_email.html', context)

        # Create text version (fallback for email clients)
        text_content = (
            f"Dear {user.get_full_name() or user.username},\n\n"
            f"The event '{event.title}' has been published and is now open for participation!\n\n"
            f"Event Details:\n"
            f"- Date & Time: {event.start_datetime.strftime('%B %d, %Y, %I:%M %p')}\n"
            f"- Location: {event.location_display}\n"
            f"- Status: {event.get_status_display()}\n\n"
            f"View event details: {context['domain']}{event.get_absolute_url()}\n\n"
            f"If you have questions, contact the organizer at {event.organizer.email}.\n\n"
            "This is an automated email. Please do not reply."
        )

        # Create and send email
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=None,  # Uses DEFAULT_FROM_EMAIL from settings
            to=[user.email],
        )
        email.attach_alternative(html_content, "text/html")

        try:
            email.send(fail_silently=False)
            sent_count += 1
            logger.info(f"Sent email to {user.email} for event {event.title}")
        except Exception as e:
            invalid_emails.append(user.email)
            logger.error(f"Failed to send email to {user.email}: {str(e)}")

    return sent_count, invalid_emails