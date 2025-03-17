from django.shortcuts import render
from django.views.generic import TemplateView
# core/views.py
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from optimizer.models import Project


# Create your views here.
class HomeView(TemplateView):
    template_name = "core/home.html"


class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    template_name = "core/projects_list.html"
    context_object_name = "projects"
    ordering = ['-created_at']

    def get_queryset(self):
        return Project.objects.filter(user=self.request.user)



class ContactusView(TemplateView):
    template_name = "core/contactus.html"



class AboutusView(TemplateView):
    template_name = "core/aboutus.html"