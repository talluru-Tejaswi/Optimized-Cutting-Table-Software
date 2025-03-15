from django.shortcuts import render
from .algorithms import optimize_with_lp
from django.views.generic import TemplateView
from django.shortcuts import redirect

from django.urls import reverse_lazy
from django.views.generic import FormView
from .forms import NewProjectForm
from .models import Project, Piece
from django.shortcuts import render, get_object_or_404

class NewProjectView(FormView):
    template_name = "new_project.html"
    form_class = NewProjectForm

    def form_valid(self, form):
        # Create the project
        project = Project.objects.create(
            user=self.request.user,
            name=form.cleaned_data['name'],
            material_type=form.cleaned_data['material_type'],
            stock_width=form.cleaned_data['stock_width'],
            stock_height=form.cleaned_data['stock_height'],
            tool_type=form.cleaned_data['tool_type'],
            algorithm=form.cleaned_data['algorithm'],
            status='processing'
        )

        # Create Piece objects based on form data (assumes pieces info is provided)
        pieces_data = form.cleaned_data.get('pieces', [])
        for pd in pieces_data:
            Piece.objects.create(
                project=project,
                width=pd['width'],
                height=pd['height'],
                quantity=pd.get('quantity', 1)
            )

        # Run the optimization algorithm (LP approach for now)
        result = optimize_with_lp(project)

        # Save results in the project (assuming utilization field exists)
        project.utilization = result.get('utilization', 0.0)
        project.status = 'completed'
        project.save()

        # Redirect to the project detail view
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('optimizer:project_detail', kwargs={'project_id': self.object.id})


class OptimizeResultView(TemplateView):
    template_name = "project_detail.html"

    def get(self, request, project_id):
        project = get_object_or_404(Project, pk=project_id, user=request.user)
        context = {"project": project}
        return render(request, self.template_name, context)
