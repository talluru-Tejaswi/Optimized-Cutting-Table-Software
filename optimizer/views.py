from django.shortcuts import render
from .algorithms import optimize_with_lp, optimize_with_ga
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
        # 1) Create Project
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

        # 2) Create Pieces
        pieces_data = form.cleaned_data['pieces']  # e.g. a list of dicts or parse from text
        for pd in pieces_data:
            Piece.objects.create(
                project=project,
                width=pd['width'],
                height=pd['height'],
                quantity=pd['quantity']
            )

        # 3) Run the chosen algorithm (synchronously for demonstration)
        algo = form.cleaned_data['algorithm']
        if algo == 'LP':
            result = optimize_with_lp(project)
        elif algo == 'GA':
            result = optimize_with_ga(project)
        else:
            # placeholder for a hybrid approach
            result = optimize_with_lp(project)  # or a real hybrid function

        # 4) Store results in the project
        project.status = 'completed'
        project.utilization = result['utilization']  # assume we have a field
        # Could store layout as JSON if you have a JSONField
        # project.layout_data = json.dumps(result['layout'])
        project.save()

        # 5) Redirect to detail page
        return redirect('optimizer:project_detail', project_id=project.id)


class OptimizeResultView(TemplateView):
    template_name = "project_detail.html"

    def get(self, request, project_id):
        project = get_object_or_404(Project, pk=project_id, user=request.user)
        context = {"project": project}
        return render(request, self.template_name, context)
