# resources/urls.py
from django.urls import path
from .views import ResourceDetailView, download_resource

urlpatterns = [
    path('<uuid:pk>/', ResourceDetailView.as_view(), name='resource_detail'),
    path('<uuid:pk>/download/', download_resource, name='resource_download'),
]