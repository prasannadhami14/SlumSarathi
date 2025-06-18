from django import forms
from .models import Service, ServiceImage, ServiceRequest, ServiceReview

class ServiceForm(forms.ModelForm):
    image = forms.ImageField(required=False, label="Service Image")  # Add this line

    class Meta:
        model = Service
        fields = [
            'title', 'slug', 'description', 'service_type',
            'pricing_model', 'rate', 'is_available', 'available_from', 'available_to'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Service Title'}),
            'slug': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'service-title', 'readonly': True}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Describe your service...', 'rows': 4}),
            'service_type': forms.Select(attrs={'class': 'form-select'}),
            # 'category': forms.Select(attrs={'class': 'form-select'}),
            'pricing_model': forms.Select(attrs={'class': 'form-select'}),
            'rate': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter rate'}),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'available_from': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'available_to': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

class ServiceImageForm(forms.ModelForm):
    class Meta:
        model = ServiceImage
        fields = ['image', 'caption', 'is_featured', 'order']
        widgets = {
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'caption': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Image caption'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Order'}),
        }

class ServiceRequestForm(forms.ModelForm):
    class Meta:
        model = ServiceRequest
        fields = ['message', 'proposed_rate']
        widgets = {
            'message': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Your message...', 'rows': 3}),
            'proposed_rate': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Proposed rate'}),
        }

class ServiceReviewForm(forms.ModelForm):
    class Meta:
        model = ServiceReview
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Your review...', 'rows': 3}),
        }