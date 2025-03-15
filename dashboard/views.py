# dashboard/views.py

import json
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView
from optimizer.models import Project

class ProjectVisualizationView(DetailView):
    model = Project
    template_name = "project_visualization.html"
    pk_url_kwarg = 'pk'

    def get_object(self):
        return get_object_or_404(Project, pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            layout_data = json.loads(self.object.layout_data or "[]")
        except:
            layout_data = []

        # Compute the midpoints in Python
        for item in layout_data:
            if item.get('placed'):
                # x_mid = x + width/2
                item['x_mid'] = item['x'] + (item['width'] / 2.0)
                # y_mid = y + height/2
                item['y_mid'] = item['y'] + (item['height'] / 2.0)
            else:
                item['x_mid'] = 0
                item['y_mid'] = 0

        context['layout_data'] = layout_data
        context['stock_width'] = self.object.stock_width
        context['stock_height'] = self.object.stock_height
        return context
