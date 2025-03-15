from django.db import models
from django.contrib.auth.models import User

from django.db import models
from django.contrib.auth.models import User

class Project(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')
    name = models.CharField(max_length=100)
    material_type = models.CharField(max_length=50)
    stock_width = models.FloatField()
    stock_height = models.FloatField()
    tool_type = models.CharField(max_length=50, blank=True, null=True)
    algorithm = models.CharField(max_length=20, blank=True, null=True)
    status = models.CharField(max_length=20, default='processing')
    utilization = models.FloatField(default=0.0)  # optional field for storing result
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Piece(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='pieces')
    width = models.FloatField()
    height = models.FloatField()
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'Piece (W={self.width}, H={self.height}, Qty={self.quantity})'
