
from django.urls import path
from .views import ProjectVisualizationView

app_name = 'dashboard'

urlpatterns = [
    path('project/<int:pk>/visual/', ProjectVisualizationView.as_view(), name='project_visual'),

]