from django.urls import path
from .views import (LoginView, RegisterView, LogoutView, EmailVerificationView,
                    DashboardView, ProfileUpdateView)

urlpatterns = [
    path('authenticate/v1/login/', LoginView.as_view(), name='login'),
    path('authenticate/v1/register/', RegisterView.as_view(), name='register'),
    path('authenticate/v1/logout/', LogoutView.as_view(), name='logout'),
    path('authenticate/v1/verify-email/<str:token>/', EmailVerificationView.as_view(), name='verify_email'),
    path('authenticate/v1/dashboard/', DashboardView.as_view(), name='dashboard'),
    path('authenticate/v1/profile-update/', ProfileUpdateView.as_view(), name='profile_update'),
]
