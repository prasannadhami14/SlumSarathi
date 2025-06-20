from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Event, EventRegistration
from .tasks import send_event_published_email_task  # Import the task

@receiver(pre_save, sender=Event)
def cache_old_status(sender, instance, **kwargs):
    if instance.pk:
        old_instance = Event.objects.get(pk=instance.pk)
        instance._old_status = old_instance.status
    else:
        instance._old_status = None
@receiver(post_save, sender=Event)
def send_published_event_notification(sender, instance, created, update_fields=None, **kwargs):
    try:
        print("Signal fired for event:", instance.id)
        if not created and update_fields and 'status' in update_fields:
            print("Status in update_fields, current status:", instance.status)
            print("Old status (from pre_save):", getattr(instance, '_old_status', None))
            if hasattr(instance, '_old_status') and instance._old_status != 'published' and instance.status == 'published':
                print("Status changed to published, calling Celery task!")
                registrations = EventRegistration.objects.filter(event=instance)
                user_ids = [str(reg.user.id) for reg in registrations if reg.user.email]
                print("User IDs to notify:", user_ids)
                if user_ids:
                    print("Calling Celery task!")
                    send_event_published_email_task.delay(
                        str(instance.id),
                        user_ids,
                        'localhost:8000'
                    )
    except Event.DoesNotExist:
        print("Old instance does not exist")