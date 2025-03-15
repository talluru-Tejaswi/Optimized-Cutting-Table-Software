from django.contrib import admin
from .models import ToolConfig, FurnitureTemplate, Project, Piece

@admin.register(ToolConfig)
class ToolConfigAdmin(admin.ModelAdmin):
    list_display = ('name', 'tool_type', 'size', 'speed', 'power', 'focus')
    list_filter = ('tool_type',)
    search_fields = ('name',)

@admin.register(FurnitureTemplate)
class FurnitureTemplateAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'material_type', 'stock_width', 'stock_height', 'tool_config', 'furniture_template', 'status', 'utilization', 'created_at')
    list_filter = ('status', 'material_type', 'tool_config__tool_type', 'furniture_template')
    search_fields = ('name', 'user__username')
    ordering = ('-created_at',)

@admin.register(Piece)
class PieceAdmin(admin.ModelAdmin):
    list_display = ('project', 'label', 'width', 'height', 'quantity')
    list_filter = ('project',)
    search_fields = ('project__name', 'label')
