from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.utils.translation import gettext as _
from .models import Service, ServiceCategory, ServiceImage, ServiceRequest, ServiceReview
from .forms import (
    ServiceForm, ServiceImageForm, ServiceRequestForm, ServiceReviewForm
)
from django.http import JsonResponse
from django.template.loader import render_to_string

def service_list(request):
    query = request.GET.get('q', '')
    services = Service.objects.filter(is_available=True)
    if query:
        services = services.filter(title__icontains=query)
    categories = ServiceCategory.objects.all()
    return render(request, 'services/service_list.html', {
        'services': services,
        'categories': categories,
        'query': query,
        'search_scope': 'services',
    })

# def service_list_by_category(request, slug):
#     category = get_object_or_404(ServiceCategory, slug=slug)
#     services = Service.objects.filter(category=category, is_available=True)
#     categories = ServiceCategory.objects.all()
#     return render(request, 'services/service_list.html', {
#         'services': services,
#         'category': category,
#         'categories': categories
#     })

def service_detail(request, pk):
    service = get_object_or_404(Service, pk=pk)
    service.views += 1
    service.save(update_fields=['views'])
    images = service.images.all()
    reviews = service.reviews.all()
    can_review = request.user.is_authenticated and not service.reviews.filter(reviewer=request.user).exists()
    return render(request, 'services/service_detail.html', {
        'service': service,
        'images': images,
        'reviews': reviews,
        'can_review': can_review
    })

@login_required
def service_create(request):
    if request.method == 'POST':
        form = ServiceForm(request.POST, request.FILES)
        if form.is_valid():
            service = form.save(commit=False)
            service.provider = request.user
            service.save()
            # Save image if provided
            image = form.cleaned_data.get('image')
            if image:
                ServiceImage.objects.create(service=service, image=image)
            messages.success(request, "Service created successfully.")
            return redirect('services:service_detail', pk=service.pk)
    else:
        form = ServiceForm()
    return render(request, 'services/service_form.html', {'form': form})

@login_required
def service_edit(request, pk):
    service = get_object_or_404(Service, pk=pk, provider=request.user)
    if request.method == 'POST':
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            messages.success(request, _("Service updated successfully."))
            return redirect('services:service_detail', pk=service.pk)
    else:
        form = ServiceForm(instance=service)
    return render(request, 'services/service_form.html', {'form': form, 'service': service})

@login_required
def service_delete(request, pk):
    service = get_object_or_404(Service, pk=pk, provider=request.user)
    if request.method == 'POST':
        service.delete()
        messages.success(request, _("Service deleted."))
        return redirect('services:service_list')
    return render(request, 'services/service_confirm_delete.html', {'service': service})

@login_required
def service_image_add(request, service_id):
    service = get_object_or_404(Service, pk=service_id, provider=request.user)
    if request.method == 'POST':
        form = ServiceImageForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.save(commit=False)
            image.service = service
            if image.is_featured:
                # Only one featured image per service
                ServiceImage.objects.filter(service=service, is_featured=True).update(is_featured=False)
            image.save()
            messages.success(request, _("Image added."))
            return redirect('services:service_detail', pk=service.pk)
    else:
        form = ServiceImageForm()
    return render(request, 'services/service_image_form.html', {'form': form, 'service': service})

@login_required
def service_image_delete(request, image_id):
    image = get_object_or_404(ServiceImage, pk=image_id, service__provider=request.user)
    service_pk = image.service.pk
    image.delete()
    messages.success(request, _("Image deleted."))
    return redirect('services:service_detail', pk=service_pk)

@login_required
def service_request_create(request, service_id):
    service = get_object_or_404(Service, pk=service_id)
    if service.provider == request.user:
        messages.error(request, _("You cannot request your own service."))
        return redirect('services:service_detail', pk=service.pk)
    if ServiceRequest.objects.filter(service=service, requester=request.user, status='pending').exists():
        messages.error(request, _("You already have a pending request for this service."))
        return redirect('services:service_detail', pk=service.pk)
    if request.method == 'POST':
        form = ServiceRequestForm(request.POST)
        if form.is_valid():
            req = form.save(commit=False)
            req.service = service
            req.requester = request.user
            req.save()
            messages.success(request, _("Request sent."))
            return redirect('services:my_service_requests')
    else:
        form = ServiceRequestForm()
    return render(request, 'services/service_request_form.html', {'form': form, 'service': service})

@login_required
def my_service_requests(request):
    requests = ServiceRequest.objects.filter(requester=request.user)
    return render(request, 'services/service_request_list.html', {'requests': requests})

@login_required
def incoming_service_requests(request):
    # Requests for services where the current user is the provider
    requests = ServiceRequest.objects.filter(service__provider=request.user).select_related('service', 'requester')
    return render(request, 'services/incoming_service_request_list.html', {'requests': requests})

@login_required
def service_request_accept(request, request_id):
    req = get_object_or_404(ServiceRequest, pk=request_id, service__provider=request.user)
    try:
        req.accept()
        messages.success(request, _("Request accepted."))
    except Exception as e:
        messages.error(request, str(e))
    return redirect('services:my_service_requests')

@login_required
def service_request_reject(request, request_id):
    req = get_object_or_404(ServiceRequest, pk=request_id, service__provider=request.user)
    try:
        req.reject()
        messages.success(request, _("Request rejected."))
    except Exception as e:
        messages.error(request, str(e))
    return redirect('services:my_service_requests')

@login_required
def service_request_cancel(request, request_id):
    req = get_object_or_404(ServiceRequest, pk=request_id, requester=request.user)
    if req.status == 'pending':
        req.status = 'cancelled'
        req.save()
        messages.success(request, _("Request cancelled."))
    else:
        messages.error(request, _("Only pending requests can be cancelled."))
    return redirect('services:my_service_requests')

@login_required
def service_review_create(request, service_id):
    service = get_object_or_404(Service, pk=service_id)
    if ServiceReview.objects.filter(service=service, reviewer=request.user).exists():
        messages.error(request, _("You have already reviewed this service."))
        return redirect('services:service_detail', pk=service.pk)
    if request.method == 'POST':
        form = ServiceReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.service = service
            review.reviewer = request.user
            review.save()
            messages.success(request, _("Review submitted."))
            return redirect('services:service_detail', pk=service.pk)
    else:
        form = ServiceReviewForm()
    return render(request, 'services/service_review_form.html', {'form': form, 'service': service})

@login_required
def service_review_edit(request, review_id):
    review = get_object_or_404(ServiceReview, pk=review_id, reviewer=request.user)
    if request.method == 'POST':
        form = ServiceReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, _("Review updated."))
            return redirect('services:service_detail', pk=review.service.pk)
    else:
        form = ServiceReviewForm(instance=review)
    return render(request, 'services/service_review_form.html', {'form': form, 'service': review.service})

@login_required
def service_review_delete(request, review_id):
    review = get_object_or_404(ServiceReview, pk=review_id, reviewer=request.user)
    service_pk = review.service.pk
    review.delete()
    messages.success(request, _("Review deleted."))
    return redirect('services:service_detail', pk=service_pk)

def ajax_service_search(request):
    query = request.GET.get('q', '')
    services = Service.objects.filter(is_available=True)
    if query:
        services = services.filter(title__icontains=query)
    html = render_to_string('services/_service_list_items.html', {'services': services})
    return JsonResponse({'html': html})

@login_required
def notification_count(request):
    # Count incoming service requests for the current user (as provider)
    count = ServiceRequest.objects.filter(service__provider=request.user, status='pending').count()
    return JsonResponse({'count': count})
