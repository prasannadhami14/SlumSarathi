from django.urls import path
from . import views

app_name = "services"

urlpatterns = [
    # Service listing and detail
    path('', views.service_list, name='service_list'),
    path('category/<slug:slug>/', views.service_list_by_category, name='service_list_by_category'),
    path('service/<uuid:pk>/', views.service_detail, name='service_detail'),

    # Service CRUD
    path('service/create/', views.service_create, name='service_create'),
    path('service/<uuid:pk>/edit/', views.service_edit, name='service_edit'),
    path('service/<uuid:pk>/delete/', views.service_delete, name='service_delete'),

    # Service images
    path('service/<uuid:service_id>/images/add/', views.service_image_add, name='service_image_add'),
    path('service/image/<int:image_id>/delete/', views.service_image_delete, name='service_image_delete'),

    # Service requests
    path('service/<uuid:service_id>/request/', views.service_request_create, name='service_request_create'),
    path('requests/', views.my_service_requests, name='my_service_requests'),
    path('request/<uuid:request_id>/accept/', views.service_request_accept, name='service_request_accept'),
    path('request/<uuid:request_id>/reject/', views.service_request_reject, name='service_request_reject'),
    path('request/<uuid:request_id>/cancel/', views.service_request_cancel, name='service_request_cancel'),

    # Service reviews
    path('service/<uuid:service_id>/review/', views.service_review_create, name='service_review_create'),
    path('review/<int:review_id>/edit/', views.service_review_edit, name='service_review_edit'),
    path('review/<int:review_id>/delete/', views.service_review_delete, name='service_review_delete'),
]