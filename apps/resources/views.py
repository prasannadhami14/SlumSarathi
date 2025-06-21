# resources/views.py
from django import forms
from django.shortcuts import render, get_object_or_404, redirect
from django.http import FileResponse, Http404, HttpResponseForbidden, JsonResponse
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.urls import reverse
from django.contrib import messages
from django.template.loader import render_to_string
from .models import Resource, ResourceComment, ResourceRating, ResourceCategory, ResourceDownload
from .forms import ResourceUploadForm  # You need to create this form
from django.utils.text import slugify
import uuid

class ResourceUploadForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = [
            'title', 'description','thumbnail', 'file', 'resource_type',
            'course_name', 'institution', 'year', 'license_type'
        ]

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            if not file.name.lower().endswith('.pdf'):
                raise forms.ValidationError("Only PDF files are allowed.")
        return file

class ResourceListView(View):
    def get(self, request):
        query = request.GET.get('q', '')
        category_id = request.GET.get('category', '')
        resources = Resource.objects.filter(is_approved=True)
        categories = ResourceCategory.objects.all()
        if query:
            resources = resources.filter(title__icontains=query)
        if category_id:
            resources = resources.filter(category_id=category_id)
        return render(request, 'resources/resources_list.html', {
            'resources': resources,
            'categories': categories,
            'search_scope': 'resources',
        })

class ResourceDetailView(View):
    def get(self, request, pk):
        resource = get_object_or_404(Resource, pk=pk, is_approved=True)
        resource.increment_view()
        comments = resource.comments.filter(is_approved=True)
        ratings = resource.ratings.all()
        user_rating = None
        if request.user.is_authenticated:
            user_rating = ratings.filter(user=request.user).first()
        return render(request, 'resources/resources_detail.html', {
            'resource': resource,
            'comments': comments,
            'ratings': ratings,
            'user_rating': user_rating,
            'rating_choices': ResourceRating.RATING_CHOICES,
        })

    def post(self, request, pk):
        resource = get_object_or_404(Resource, pk=pk, is_approved=True)
        # Handle comment
        if 'add_comment' in request.POST and request.user.is_authenticated:
            content = request.POST.get('comment', '').strip()
            if content:
                ResourceComment.objects.create(
                    resource=resource,
                    user=request.user,
                    content=content
                )
                messages.success(request, "Comment added!")
            return redirect('resources:resource_detail', pk=pk)
        # Handle rating
        if 'add_rating' in request.POST and request.user.is_authenticated:
            rating_val = int(request.POST.get('rating', 0))
            if 1 <= rating_val <= 5:
                rating_obj, created = ResourceRating.objects.update_or_create(
                    resource=resource,
                    user=request.user,
                    defaults={'rating': rating_val}
                )
                messages.success(request, "Rating submitted!")
            return redirect('resources:resource_detail', pk=pk)
        return self.get(request, pk)

@method_decorator(login_required, name='dispatch')
class ResourceUploadView(View):
    def get(self, request):
        form = ResourceUploadForm()
        return render(request, 'resources/resources_upload.html', {'form': form})

    def post(self, request):
        form = ResourceUploadForm(request.POST, request.FILES)
        if form.is_valid():
            resource = form.save(commit=False)
            resource.uploader = request.user
            resource.is_approved = True  # Or False if you want admin approval
            resource.save()
            messages.success(request, "Resource uploaded successfully!")
            return redirect('resources:resource_detail', pk=resource.pk)
        return render(request, 'resources/resources_upload.html', {'form': form})

@login_required
def download_resource(request, pk):
    resource = get_object_or_404(Resource, pk=pk, is_approved=True)
    if not resource.allow_download:
        raise Http404("Download not allowed.")
    response = FileResponse(resource.file.open('rb'), as_attachment=True, filename=resource.file.name.split('/')[-1])
    response['Content-Type'] = 'application/pdf'
    return response

@method_decorator(login_required, name='dispatch')
class ResourceEditView(View):
    def get(self, request, pk):
        resource = get_object_or_404(Resource, pk=pk, uploader=request.user)
        form = ResourceUploadForm(instance=resource)
        return render(request, 'resources/resources_edit.html', {'form': form, 'resource': resource})

    def post(self, request, pk):
        resource = get_object_or_404(Resource, pk=pk, uploader=request.user)
        form = ResourceUploadForm(request.POST, request.FILES, instance=resource)
        if form.is_valid():
            resource = form.save(commit=False)
            # Optionally update slug if title changed
            if not resource.slug or slugify(resource.title) != resource.slug:
                base_slug = slugify(resource.title)
                unique_slug = base_slug
                while Resource.objects.filter(slug=unique_slug).exclude(pk=resource.pk).exists():
                    unique_slug = f"{base_slug}-{uuid.uuid4().hex[:6]}"
                resource.slug = unique_slug
            resource.save()
            messages.success(request, "Resource updated successfully!")
            return redirect('resources:resource_detail', pk=resource.pk)
        return render(request, 'resources/resources_edit.html', {'form': form, 'resource': resource})

@method_decorator(login_required, name='dispatch')
class ResourceDeleteView(View):
    def get(self, request, pk):
        resource = get_object_or_404(Resource, pk=pk, uploader=request.user)
        return render(request, 'resources/resource_confirm_delete.html', {'resource': resource})

    def post(self, request, pk):
        resource = get_object_or_404(Resource, pk=pk, uploader=request.user)
        resource.delete()
        messages.success(request, "Resource deleted successfully!")
        return redirect('resources:resource_list')

def ajax_resource_search(request):
    query = request.GET.get('q', '')
    resources = Resource.objects.filter(is_approved=True)
    if query:
        resources = resources.filter(title__icontains=query)
    
    # Render the resources list items as HTML
    html = render_to_string('resources/_resource_list_items.html', {
        'resources': resources,
    }, request=request)
    
    return JsonResponse({'html': html})