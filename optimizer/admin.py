from django.contrib import admin
from .models import ToolConfig, FurnitureTemplate, Project, Piece

class ToolConfigAdmin(admin.ModelAdmin):
    list_display = ('name', 'tool_type', 'get_size', 'speed', 'power', 'focus', 'description')
    
    def get_size(self, obj):
        if obj.thickness:
            return f"{obj.thickness} mm"
        return "N/A"
    get_size.short_description = "Size"

admin.site.register(ToolConfig, ToolConfigAdmin)

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
