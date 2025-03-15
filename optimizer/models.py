from django.db import models
from django.contrib.auth.models import User

class ToolConfig(models.Model):
    TOOL_CHOICES = [
        ('blade', 'Blade'),
        ('laser', 'Laser'),
    ]
    name = models.CharField(max_length=100, unique=True)
    tool_type = models.CharField(max_length=10, choices=TOOL_CHOICES)
    size = models.FloatField(help_text="Blade thickness or Laser beam diameter")
    speed = models.FloatField(help_text="Cutting speed in mm/s")
    power = models.FloatField(null=True, blank=True, help_text="Laser power if tool_type=laser")
    focus = models.FloatField(null=True, blank=True, help_text="Laser focus if tool_type=laser")

    def __str__(self):
        return f"{self.name} ({self.tool_type})"

class FurnitureTemplate(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    default_pieces = models.TextField(help_text="JSON list of pieces. E.g.: " +
                                      '[{"label": "Leg", "width": 50, "height": 50, "quantity": 4}, ' +
                                      '{"label": "Top", "width": 100, "height": 60, "quantity": 1}]')

    def __str__(self):
        return self.name

class Project(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')
    name = models.CharField(max_length=100)
    material_type = models.CharField(max_length=50)
    stock_width = models.FloatField()
    stock_height = models.FloatField()
    tool_config = models.ForeignKey(ToolConfig, on_delete=models.SET_NULL, null=True)
    furniture_template = models.ForeignKey(FurnitureTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, default='processing')
    utilization = models.FloatField(default=0.0)
    layout_data = models.TextField(blank=True, null=True)   # JSON storing piece placements
    assembly_steps = models.TextField(blank=True, null=True)  # JSON storing step-by-step instructions
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Piece(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='pieces')
    label = models.CharField(max_length=100, blank=True)   # E.g., "Leg", "Top"
    width = models.FloatField()
    height = models.FloatField()
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.label or 'Piece'} ({self.width}x{self.height} x{self.quantity})"
