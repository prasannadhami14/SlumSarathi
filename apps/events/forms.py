from django import forms
from .models import Event
from django.utils import timezone
from django.core.exceptions import ValidationError

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            'title', 'description', 'event_type',
            'start_datetime', 'end_datetime', 'registration_deadline',
            'venue_name', 'address', 'city', 'state', 'country', 'online_link',
            'capacity', 'is_free', 'price', 'featured_image', 'status'  # Added status field
        ]
        widgets = {
            'start_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'registration_deadline': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 4}),
            'address': forms.Textarea(attrs={'rows': 2}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_datetime = cleaned_data.get('start_datetime')
        end_datetime = cleaned_data.get('end_datetime')
        registration_deadline = cleaned_data.get('registration_deadline')
        event_type = cleaned_data.get('event_type')
        online_link = cleaned_data.get('online_link')

        if start_datetime and end_datetime and start_datetime > end_datetime:
            raise ValidationError("End datetime must be after start datetime")

        if registration_deadline and start_datetime and registration_deadline > start_datetime:
            raise ValidationError("Registration deadline cannot be after event start")

        if event_type == 'online' and not online_link:
            raise ValidationError("Online events must have a link")

        return cleaned_data