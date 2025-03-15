from django.contrib import admin
from django.urls import path

from optimizer.views import NewProjectView, OptimizeResultView
app_name = 'optimizer'

urlpatterns = [
     path('new/', NewProjectView.as_view(), name='new_project'),
    path('<int:project_id>/', OptimizeResultView.as_view(), name='project_detail'),
]