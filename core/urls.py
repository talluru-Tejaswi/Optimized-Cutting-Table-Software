from django.contrib import admin
from django.urls import path
from .views import HomeView, ProjectListView,ContactusView,AboutusView

urlpatterns = [
    path("", HomeView.as_view(), name="home"),  # Maps to the root URL
    path('info/v1/about/', AboutusView.as_view(), name='aboutus'),
    path('info/v1/contact/', ContactusView.as_view(), name='contactus'),
    path('dashboard/v1/projects/', ProjectListView.as_view(), name='project_list'),
]