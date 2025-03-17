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
from django.contrib.auth.mixins import LoginRequiredMixin
from plotly.offline import plot
import plotly.graph_objs as go
import logging

# optimizer/views.py

import json
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView
from .models import Project

logger = logging.getLogger(__name__)

class ProjectDetail3DView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = "optimizer/project_detail_3d.html"
    context_object_name = "project"
    pk_url_kwarg = "pk"

    def get_object(self):
        """
        Ensure only the owner can see their project's 3D view
        (or modify logic for public projects if desired).
        """
        return get_object_or_404(Project, pk=self.kwargs["pk"], user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 1) Parse layout_data from the DB (JSON string of piece placements)
        layout_json = self.object.layout_data or "[]"
        try:
            layout = json.loads(layout_json)
        except:
            layout = []

        # 2) Decide how you want to 'stack' or 'fly' each piece
        #    e.g., each subsequent piece gets an extra 10 units in Z
        step_height = 10.0
        piece_thickness = 5.0

        # We'll store each piece as a "box" with corners, plus separate label points
        piece_boxes = []
        label_points = []

        for i, item in enumerate(layout):
            # Skip if piece wasn't placed
            if not item.get("placed"):
                continue

            # Offsets in the Z direction
            z_base = i * step_height
            z_top  = z_base + piece_thickness

            x0 = item["x"]
            y0 = item["y"]
            w  = item["width"]
            h  = item["height"]

            # Create a box from (x0, y0, z_base) to (x0+w, y0+h, z_top)
            piece_boxes.append({
                "piece_id":    item["piece_id"],
                "x0": x0,       "y0": y0,       "z0": z_base,
                "x1": x0 + w,   "y1": y0 + h,   "z1": z_top
            })

            # We'll also store a label coordinate above the box top
            label_points.append({
                "x": x0 + w/2.0,
                "y": y0 + h/2.0,
                "z": z_top + 2.0,  # a bit above the piece
                "text": f"Piece {item['piece_id']}"
            })

        # 3) (Optional) If you want a base 'stock' box:
        stock_w = self.object.stock_width
        stock_h = self.object.stock_height
        stock_box = {
            "x0": 0,          "y0": 0,          "z0": 0,
            "x1": stock_w,    "y1": stock_h,    "z1": 1.0,  # thin base
        }

        # 4) We'll pass all these to the template so it can build a Plotly figure
        context["layout_data_3d"] = {
            "pieces": piece_boxes,        # the box corners for each piece
            "labels": label_points,       # label coords
            "stock": stock_box,           # optional base sheet
            "stock_width":  stock_w,
            "stock_height": stock_h,
            # an approximate max z-range if you want to set camera or axis
            "max_z": len(piece_boxes) * step_height + piece_thickness + 10
        }

        return context




class NewProjectView(FormView):
    template_name = "optimizer/new_project.html"
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
        print("DEBUG: Algorithm returned:", result) 
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
    template_name = "optimizer/project_detail.html"
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

    html_string = render_to_string('optimizer/export_report.html', {
        'project': project,
        'layout': layout,
        'steps': steps,
    })
    pdf_file = weasyprint.HTML(string=html_string).write_pdf()
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Project_{pk}_Report.pdf"'
    return response
