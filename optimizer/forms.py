from django import forms
from .models import Project, ToolConfig, FurnitureTemplate

MATERIAL_CHOICES = [
    ('wood', 'Wood'),
    ('metal', 'Metal'),
    ('plastic', 'Plastic'),
]

class NewProjectForm(forms.ModelForm):
    material_type = forms.ChoiceField(choices=MATERIAL_CHOICES)
    tool_config = forms.ModelChoiceField(
        queryset=ToolConfig.objects.all(),
        required=True,
        label="Tool Configuration"
    )
    furniture_template = forms.ModelChoiceField(
        queryset=FurnitureTemplate.objects.all(),
        required=False,
        label="Furniture Template",
        help_text="Choose a template to auto-generate default pieces."
    )
    custom_pieces = forms.CharField(
        widget=forms.Textarea,
        required=False,
        help_text="Optional. Enter custom pieces as: 50x30:2, 40x10:3"
    )

    class Meta:
        model = Project
        fields = ['name', 'material_type', 'stock_width', 'stock_height', 'tool_config', 'furniture_template', 'custom_pieces']
