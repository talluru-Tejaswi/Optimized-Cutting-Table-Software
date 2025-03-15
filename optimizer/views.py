import json
import weasyprint

from django.http import HttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import FormView, DetailView
from .forms import NewProjectForm
from .models import Project, Piece
from .algorithms import optimize_with_lp, optimize_with_ga
from django.template.loader import render_to_string

# optimizer/views.py

import json
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView
from .models import Project

class ProjectDetail3DView(DetailView):
    model = Project
    template_name = "project_detail_3d.html"
    context_object_name = 'project'
    pk_url_kwarg = 'pk'

    def get_object(self):
        # If you want to restrict to the current user:
        return get_object_or_404(Project, pk=self.kwargs['pk'], user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['layout_data'] = json.loads(self.object.layout_data or "[]")
        except:
            context['layout_data'] = []
        return context



class NewProjectView(FormView):
    template_name = "new_project.html"
    form_class = NewProjectForm

    def form_valid(self, form):
        # Create the project
        project = form.save(commit=False)
        project.user = self.request.user
        project.status = 'processing'
        project.save()

        # If a FurnitureTemplate is chosen, auto-create pieces from its default JSON
        if project.furniture_template:
            try:
                default_pieces = json.loads(project.furniture_template.default_pieces)
                for p in default_pieces:
                    Piece.objects.create(
                        project=project,
                        label=p.get('label', ''),
                        width=p['width'],
                        height=p['height'],
                        quantity=p['quantity']
                    )
            except Exception as e:
                print("Error parsing furniture template:", e)

        # If custom pieces are provided, parse them (format: "50x30:2, 40x10:3")
        custom_str = form.cleaned_data.get('custom_pieces', '')
        if custom_str:
            for part in custom_str.split(','):
                try:
                    part = part.strip()
                    dims, qty = part.split(':')
                    width, height = dims.split('x')
                    Piece.objects.create(
                        project=project,
                        label="Custom",
                        width=float(width),
                        height=float(height),
                        quantity=int(qty)
                    )
                except Exception as e:
                    print("Error parsing custom piece:", e)
                    continue

        # Run the chosen algorithm: For example, use GA for laser, LP for blade.
        if project.tool_config.tool_type == 'laser':
            result = optimize_with_ga(project)
        else:
            result = optimize_with_lp(project)

        project.layout_data = json.dumps(result.get('layout', []))
        project.utilization = result.get('utilization', 0.0)
        project.status = 'completed'
        # Optional: store assembly steps based on furniture template (example for table)
        if project.furniture_template and project.furniture_template.name.lower() == 'table':
            project.assembly_steps = json.dumps([
                "Attach the four legs to the tabletop at each corner.",
                "Secure with screws or adhesive.",
                "Check alignment and stability."
            ])
        project.save()

        return redirect('optimizer:project_detail', pk=project.pk)

class ProjectDetailView(DetailView):
    model = Project
    template_name = "project_detail.html"
    context_object_name = 'project'
    pk_url_kwarg = 'pk'

    def get_object(self):
        return get_object_or_404(Project, pk=self.kwargs['pk'], user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['layout_data'] = json.loads(self.object.layout_data or "[]")
        except:
            context['layout_data'] = []
        try:
            context['assembly_steps'] = json.loads(self.object.assembly_steps or "[]")
        except:
            context['assembly_steps'] = []
        return context

def export_report(request, pk):
    project = get_object_or_404(Project, pk=pk, user=request.user)
    try:
        layout = json.loads(project.layout_data or "[]")
    except:
        layout = []
    # Compute midpoints in Python
    for item in layout:
        if item.get('placed'):
            item['x_mid'] = item['x'] + (item['width'] / 2.0)
            item['y_mid'] = item['y'] + (item['height'] / 2.0)
        else:
            item['x_mid'] = 0
            item['y_mid'] = 0

    try:
        steps = json.loads(project.assembly_steps or "[]")
    except:
        steps = []

    html_string = render_to_string('export_report.html', {
        'project': project,
        'layout': layout,
        'steps': steps,
    })
    pdf_file = weasyprint.HTML(string=html_string).write_pdf()
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Project_{pk}_Report.pdf"'
    return response
