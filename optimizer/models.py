from django.db import models
from django.contrib.auth.models import User

TOOL_TYPE_CHOICES = [
    ('blade', 'Blade'),
    ('laser', 'Laser'),
]

class ToolConfig(models.Model):
    name = models.CharField(max_length=100, unique=True)
    tool_type = models.CharField(max_length=10, choices=TOOL_TYPE_CHOICES)
    thickness = models.FloatField(
        null=True, blank=True, 
        help_text="Blade thickness or Laser beam diameter (mm)"
    )
    speed = models.FloatField(
        null=True, blank=True, 
        help_text="Cutting speed in mm/s"
    )
    power = models.FloatField(
        null=True, blank=True, 
        help_text="Laser power if tool_type=laser (Watts)"
    )
    focus = models.FloatField(
        null=True, blank=True, 
        help_text="Laser focus if tool_type=laser (mm offset)"
    )
    notes = models.TextField(
        null=True, blank=True, 
        help_text="Any extra details"
    )
    description = models.TextField(
        null=True, blank=True,
        help_text="A more detailed description or usage guidelines"
    )

    def __str__(self):
        return f"{self.name} ({self.tool_type})"

class FurnitureTemplate(models.Model):
    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=100, blank=True, help_text="Category e.g. Office, Living Room")
    description = models.TextField(blank=True, help_text="Detailed description")
    default_pieces = models.TextField(blank=True, help_text="Pieces e.g. '50x30:2, 40x10:3'")

    def __str__(self):
        return self.name

    def get_default_pieces(self):
        return self.default_pieces


class Project(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')
    name = models.CharField(max_length=100)
    material_type = models.CharField(max_length=50)
    stock_width = models.FloatField()
    stock_height = models.FloatField()
    stock_depth = models.FloatField(default=5.0, help_text="Depth (thickness) of the base stock in mm")
    algorithm = models.CharField(
    max_length=20,
    default='lp',
    help_text="Optimization method: lp, ga, or hybrid"
    )
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
