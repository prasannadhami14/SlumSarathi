# resources/views.py
from django import forms
from django.shortcuts import get_object_or_404
from django.http import FileResponse, HttpResponseForbidden, JsonResponse
from django.views.generic import DetailView
from .models import Resource, ResourceDownload

class ResourceForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = ['title', 'description', 'file', 'resource_type']  # etc.
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            if not file.name.lower().endswith('.pdf'):
                raise forms.ValidationError("Only PDF files are allowed.")
            # You can also validate PDF content here if needed
            # using libraries like PyPDF2 or pdfminer
        return file
class ResourceDetailView(DetailView):
    model = Resource
    template_name = 'resources/detail.html'
    context_object_name = 'resource'
    
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.increment_view()
        return obj

def download_resource(request, pk):
    resource = get_object_or_404(Resource, pk=pk)
    
    if not resource.allow_download:
        return HttpResponseForbidden("Downloads are not allowed for this resource")
    
    # Track download
    ResourceDownload.objects.create(
        resource=resource,
        user=request.user if request.user.is_authenticated else None,
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        referrer=request.META.get('HTTP_REFERER', '')
    )
    
    resource.increment_download()
    response = FileResponse(resource.file)
    response['Content-Disposition'] = f'attachment; filename="{resource.file.name}"'
    return response
def upload_resource(request):
    if request.method == 'POST':
        # Check content type
        if request.FILES['file'].content_type != 'application/pdf':
            return JsonResponse(
                {'error': 'Invalid file type. Only PDF is allowed.'},
                status=400
            )