from django import forms
from .models import Service, ServiceImage, ServiceRequest, ServiceReview

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = [
            'title', 'slug', 'description', 'service_type', 'category',
            'pricing_model', 'rate', 'is_available', 'available_from', 'available_to'
        ]
        widgets = {
            'available_from': forms.DateInput(attrs={'type': 'date'}),
            'available_to': forms.DateInput(attrs={'type': 'date'}),
        }

class ServiceImageForm(forms.ModelForm):
    class Meta:
        model = ServiceImage
        fields = ['image', 'caption', 'is_featured', 'order']

class ServiceRequestForm(forms.ModelForm):
    class Meta:
        model = ServiceRequest
        fields = ['message', 'proposed_rate']

class ServiceReviewForm(forms.ModelForm):
    class Meta:
        model = ServiceReview
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.RadioSelect,
            'comment': forms.Textarea(attrs={'rows': 3}),
        }