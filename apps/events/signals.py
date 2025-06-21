from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Event
from .utils import send_event_published_email  # Import the utility function
from django.http import HttpRequest
from accounts.models import User  # Import your custom User model
from django.conf import settings

@receiver(pre_save, sender=Event)
def cache_old_status(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = Event.objects.get(pk=instance.pk)
            instance._old_status = old_instance.status
        except Event.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None

class DummyRequest(HttpRequest):
    def is_secure(self):
        return True  # or False if you want http

def notify_all_users_event_published(event):
    print("Notifying all users about published event!")
    users = User.objects.filter(is_active=True).exclude(email='').distinct()
    users = [user for user in users if user.email]  # Extra check for valid emails
    if users:
        request = DummyRequest()
        request.META['HTTP_HOST'] = settings.SITE_DOMAIN  # Use your domain from settings
        request.META['SERVER_PROTOCOL'] = 'https'
        send_event_published_email(event, users, request)

@receiver(post_save, sender=Event)
def send_published_event_notification(sender, instance, created, update_fields=None, **kwargs):
    try:
        print("Signal fired for event:", instance.id)
        # If event is newly created and status is published, send emails
        if created and instance.status == 'published':
                notify_all_users_event_published(instance)
        # If event is updated and status changed to published, send emails
        elif not created and update_fields and 'status' in update_fields:
            if hasattr(instance, '_old_status') and instance._old_status != 'published' and instance.status == 'published':
                notify_all_users_event_published(instance)
    except Event.DoesNotExist:
        print("Old instance does not exist")

                