from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, HTML, Field
from .models import Project, ToolConfig, FurnitureTemplate

MATERIAL_CHOICES = [
    ('wood', 'Wood'),
    ('metal', 'Metal'),
    ('plastic', 'Plastic'),
]

ALGORITHM_CHOICES = [
    ('lp', 'Linear Programming (LP)'),
    ('ga', 'Genetic Algorithm (GA)'),
    ('hybrid', 'Hybrid (LP+GA)'),
]

class NewProjectForm(forms.ModelForm):
    material_type = forms.ChoiceField(choices=MATERIAL_CHOICES)
    tool_config = forms.ModelChoiceField(
        queryset=ToolConfig.objects.all(),
        required=True,
        label="Tool Configuration"
    )
    stock_depth = forms.FloatField(
        label="Stock Base Depth (mm)",
        initial=5.0,
        min_value=0.1,
        help_text="Thickness of the base material in mm"
    )
    furniture_template = forms.ModelChoiceField(
        queryset=FurnitureTemplate.objects.all(),
        required=False,
        label="Furniture Template",
        help_text="Select a template to auto-generate default pieces."
    )
    custom_pieces = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'E.g., 50x30:2, 40x10:3'}),
        required=False,
        label="Custom Pieces",
        help_text="Optional. Enter custom pieces (overrides template default if provided)."
    )
    algorithm = forms.ChoiceField(
        choices=ALGORITHM_CHOICES,
        required=True,
        label="Optimization Method",
        help_text="Choose the optimization method to generate the cutting pattern."
    )

    class Meta:
        model = Project
        fields = [
            'name', 
            'material_type', 
            'stock_width', 
            'stock_height', 
            "stock_depth",
            'tool_config', 
            'furniture_template', 
            'custom_pieces',
            'algorithm'
        ]

    def __init__(self, *args, **kwargs):
        super(NewProjectForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'post'
        self.helper.form_action = ''
        self.helper.label_class = 'fw-bold'
        self.helper.field_class = 'mb-3'
        self.helper.layout = Layout(
            Row(
                Column('name', css_class='col-md-6'),
                Column('material_type', css_class='col-md-6')
            ),
            Row(
                Column('stock_width', css_class='col-md-6'),
                Column('stock_height', css_class='col-md-6'),
                Column('stock_depth', css_class='col-md-4'),  # ✅ Add this line

            ),
            Field('tool_config'),
            Field('furniture_template'),
            Field('custom_pieces'),
            Field('algorithm'),
            HTML("""
                <p class="small text-muted">
                    If you select a furniture template and leave custom pieces blank, 
                    we’ll auto-generate the pieces using the template's defaults.
                </p>
            """),
            Submit('submit', 'Create Project', css_class='btn btn-primary')
        )

    @staticmethod
    def parse_piece_string(piece_str):
        pieces = []
        for part in piece_str.split(","):
            part = part.strip()
            if not part:
                continue
            try:
                dims, qty = part.split(":")
                w, h = dims.split("x")
                w = float(w)
                h = float(h)
                q = int(qty)
                if w > 0 and h > 0 and q > 0:
                    pieces.append({"width": w, "height": h, "quantity": q})
            except Exception:
                continue
        return pieces


