from django.contrib import admin
from django.urls import path

from optimizer.views import NewProjectView, ProjectDetail3DView, ProjectDetailView, export_report
app_name = 'optimizer'

urlpatterns = [
    path('new/', NewProjectView.as_view(), name='new_project'),
    path('<int:pk>/', ProjectDetailView.as_view(), name='project_detail'),
    path('<int:pk>/3d/', ProjectDetail3DView.as_view(), name='project_detail_3d'),
    path('<int:pk>/export_report/', export_report, name='export_report'),

]