from services.models import ServiceRequest

def incoming_requests_notification(request):
    if request.user.is_authenticated:
        has_incoming_requests = ServiceRequest.objects.filter(
            service__provider=request.user, status='pending'
        ).exists()
    else:
        has_incoming_requests = False
    return {'has_incoming_requests': has_incoming_requests}
