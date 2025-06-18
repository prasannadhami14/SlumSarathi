from django import forms
from .models import Resource

class ResourceUploadForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = [
            'title', 'slug', 'description', 'resource_type', 'category',
            'file', 'thumbnail', 'license_type', 'is_free', 'allow_download',
            'allow_comments', 'course_name', 'institution', 'year'
        ]
        labels = {
            'course_name': 'Course',
            'institution': 'Institution',
            'year': 'Year',
            'license_type': 'License',
        }
        widgets = {
            'license_type': forms.Select(attrs={'class': 'form-select'}),
            'year': forms.NumberInput(attrs={'class': 'form-control', 'min': 1900, 'max': 2100}),
        }