# resources/urls.py
from django.urls import path
from .views import (
    ResourceListView, ResourceDetailView, ResourceUploadView, download_resource,ResourceEditView
)

app_name = "resources"

urlpatterns = [
    path('', ResourceListView.as_view(), name='resource_list'),
    path('upload/', ResourceUploadView.as_view(), name='resource_upload'),
    path('<uuid:pk>/', ResourceDetailView.as_view(), name='resource_detail'),
    path('<uuid:pk>/download/', download_resource, name='resource_download'),
    path('<uuid:pk>/edit/', ResourceEditView.as_view(), name='resource_edit'),

]