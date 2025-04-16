import json
import weasyprint
import random
from django.conf import settings
import os

from django.http import HttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import FormView, DetailView
from .forms import NewProjectForm
from .models import Project, Piece, ToolConfig
from .algorithms import OptimizerEngine
from django.template.loader import render_to_string
from django.contrib.auth.mixins import LoginRequiredMixin
import logging
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

logger = logging.getLogger(__name__)


class ProjectDetail3DView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = "optimizer/project_detail_3d.html"
    context_object_name = "project"
    pk_url_kwarg = "pk"

    def get_object(self):
        return get_object_or_404(Project, pk=self.kwargs["pk"], user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        layout_json = self.object.layout_data or "[]"
        try:
            layout = json.loads(layout_json)
        except:
            layout = []

        stock_depth = getattr(self.object, "stock_depth", 5.0)
        piece_thickness = stock_depth

        piece_boxes = []
        label_points = []

        for i, item in enumerate(layout):
            if not item.get("placed"):
                continue

            piece_id = item.get("id") or item.get("piece_id")

            x = item["x"]
            y = item["y"]
            w = item["width"]
            h = item["height"]
            z_base = item.get("z", i * stock_depth)
            z_top = z_base + piece_thickness

            piece_boxes.append({
                "piece_id": piece_id,
                "x0": x,       "y0": y,       "z0": z_base,
                "x1": x + w,   "y1": y + h,   "z1": z_top
            })

            label_points.append({
                "x": x + w/2.0,
                "y": y + h/2.0,
                "z": z_top + 2.0,
                "text": f"Piece {piece_id}"
            })

        stock_w = self.object.stock_width
        stock_h = self.object.stock_height
        stock_box = {
            "x0": 0, "y0": 0, "z0": 0,
            "x1": stock_w, "y1": stock_h, "z1": 1.0
        }

        context["layout_data_3d"] = {
            "pieces": piece_boxes,
            "labels": label_points,
            "stock": stock_box,
            "stock_width": stock_w,
            "stock_height": stock_h,
            "max_z": max([b["z1"] for b in piece_boxes] + [1]) + 10
        }
        return context


class NewProjectView(LoginRequiredMixin, FormView):
    template_name = "optimizer/new_project.html"
    form_class = NewProjectForm

    def form_valid(self, form):
        project = form.save(commit=False)
        project.user = self.request.user
        project.status = 'processing'
        project.save()

        piece_data = []
        custom = form.cleaned_data.get('custom_pieces', '').strip()
        template = project.furniture_template

        if template and not custom:
            piece_data = NewProjectForm.parse_piece_string(template.get_default_pieces())
        elif custom:
            piece_data = NewProjectForm.parse_piece_string(custom)

        for item in piece_data:
            Piece.objects.create(
                project=project,
                width=item['width'],
                height=item['height'],
                quantity=item['quantity']
            )

        engine = OptimizerEngine(project)
        method = project.algorithm.lower()

        if method == 'lp':
            result = engine.optimize_lp()
        elif method == 'ga':
            result = engine.optimize_ga()
        elif method == 'hybrid':
            result = engine.optimize_hybrid()
        else:
            raise ValueError(f"Unknown algorithm: {method}")

        project.layout_data = json.dumps(result.get('layout', []))
        project.utilization = result.get('utilization', 0.0)
        project.status = 'completed'

        # Handle instructions: Prefer optimizer-generated, fallback to template
        steps = result.get("steps")
        if steps:
            project.assembly_steps = json.dumps(steps)
        elif template:
            try:
                with open(os.path.join(settings.BASE_DIR, 'optimizer', 'fixtures', 'assembly_instructions.json')) as f:
                    instructions_map = json.load(f)
                    if template.name in instructions_map:
                        project.assembly_steps = json.dumps(instructions_map[template.name])
            except Exception as e:
                logger.warning(f"Could not load assembly instructions: {e}")
                project.assembly_steps = json.dumps([])

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

    for item in layout:
        item['id'] = item.get('piece_id', item.get('id', '?'))
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


class ProjectCompareView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = "optimizer/project_compare.html"
    context_object_name = "project"
    pk_url_kwarg = "pk"

    def get_object(self):
        return get_object_or_404(Project, pk=self.kwargs["pk"], user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from .algorithms import OptimizerEngine
        from .models import ToolConfig

        project = self.get_object()
        tool_configs = ToolConfig.objects.all()
        materials = ['wood', 'metal', 'plastic']

        engine = OptimizerEngine(project)

        # Run optimizers
        result_lp = engine.optimize_lp()
        result_ga = engine.optimize_ga()
        result_hybrid = engine.optimize_hybrid()
        print("LP layout sample:", result_lp["layout"][:2])
        print("Hybrid layout sample:", result_hybrid["layout"][:2])


        # Normalize layout
        for layout in [result_lp["layout"], result_ga["layout"], result_hybrid["layout"]]:
            for p in layout:
                if "id" not in p:
                    p["id"] = p.get("piece_id", "?")
                if p.get("placed") and all(k in p for k in ("x", "y", "width", "height")):
                    if p["width"] > 0 and p["height"] > 0:
                        p["label_x"] = p["x"] + p["width"] / 2
                        p["label_y"] = p["y"] + p["height"] / 2

        # Update context
        context.update({
            "tool_configs": tool_configs,
            "materials": materials,
            "comparisons": [
                {"method": "LP", "result": result_lp},
                {"method": "GA", "result": result_ga},
                {"method": "Hybrid", "result": result_hybrid},
            ],
            "best_method": max(
                [("LP", result_lp), ("GA", result_ga), ("Hybrid", result_hybrid)],
                key=lambda x: x[1]["utilization"]
            )[0]
        })

        return context





@require_POST
@csrf_exempt
def compare_optimizers_api(request, pk):
    from .models import Project, ToolConfig
    from .algorithms import OptimizerEngine

    try:
        project = Project.objects.get(pk=pk)
        data = json.loads(request.body)

        # Apply temporary tool/material config from user selection
        tool_id = data.get("tool_config")
        material = data.get("material")

        if tool_id:
            project.tool_config = ToolConfig.objects.get(pk=tool_id)
        if material:
            project.material_type = material.lower()

        engine = OptimizerEngine(project)

        # Run optimizers
        result_lp = engine.optimize_lp()
        result_ga = engine.optimize_ga()
        result_hybrid = engine.optimize_hybrid()

        # Normalize layout: ID & SVG text position
        for layout in [result_lp["layout"], result_ga["layout"], result_hybrid["layout"]]:
            for p in layout:
                if "id" not in p:
                    p["id"] = p.get("piece_id", "?")
                if p.get("placed") and all(k in p for k in ("x", "y", "width", "height")):
                    if p["width"] > 0 and p["height"] > 0:
                        p["label_x"] = p["x"] + p["width"] / 2
                        p["label_y"] = p["y"] + p["height"] / 2

        return JsonResponse({
            "lp": {"utilization": result_lp["utilization"], "layout": result_lp["layout"]},
            "ga": {"utilization": result_ga["utilization"], "layout": result_ga["layout"]},
            "hybrid": {"utilization": result_hybrid["utilization"], "layout": result_hybrid["layout"]},
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)