from django.urls import path
from . import views

urlpatterns = [
    # Example:
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('profile/<int:user_id>/', views.profile_view, name='profile'),
    path('edit/<int:user_id>/', views.edit_profile_view, name='edit_profile'),
]