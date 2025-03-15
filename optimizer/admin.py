from django.contrib import admin
from .models import Piece, Project

# Register your models here.
@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'user__username')

@admin.register(Piece)
class PieceAdmin(admin.ModelAdmin):
    list_display = ('project', 'width', 'height', 'quantity')