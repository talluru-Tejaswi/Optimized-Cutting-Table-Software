from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, HTML, Field
from .models import Piece, Project, ToolConfig, FurnitureTemplate

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
            'tool_config', 
            'furniture_template', 
            'custom_pieces',
            'algorithm'
        ]

    def __init__(self, *args, **kwargs):
        super(NewProjectForm, self).__init__(*args, **kwargs)
        # Initialize Crispy Forms helper
        self.helper = FormHelper(self)
        self.helper.form_method = 'post'
        self.helper.form_action = ''  # Specify URL if needed
        self.helper.label_class = 'fw-bold'
        self.helper.field_class = 'mb-3'
        self.helper.layout = Layout(
            Row(
                Column('name', css_class='col-md-6'),
                Column('material_type', css_class='col-md-6')
            ),
            Row(
                Column('stock_width', css_class='col-md-6'),
                Column('stock_height', css_class='col-md-6')
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

    def clean(self):
        cleaned_data = super().clean()
        stock_width = cleaned_data.get('stock_width')
        stock_height = cleaned_data.get('stock_height')

        if stock_width is None or stock_width <= 0:
            self.add_error('stock_width', "Stock width must be a positive number.")
        if stock_height is None or stock_height <= 0:
            self.add_error('stock_height', "Stock height must be a positive number.")

        min_dimension = 10  # or any minimum value you require
        if stock_width < min_dimension:
            self.add_error('stock_width', f"Stock width must be at least {min_dimension} units.")
        if stock_height < min_dimension:
            self.add_error('stock_height', f"Stock height must be at least {min_dimension} units.")

        return cleaned_data
    
    def parse_piece_string(piece_str):
        """
        Parse a string formatted as '50x30:2, 40x10:3' into a list of dictionaries.
        Each dictionary contains 'width', 'height', and 'quantity'.
        """
        items = []
        for part in piece_str.split(','):
            part = part.strip()
            if not part:
                continue
            try:
                dims, qty_str = part.split(':')
                w_str, h_str = dims.split('x')
                w = float(w_str)
                h = float(h_str)
                qty = int(qty_str)
                items.append({'width': w, 'height': h, 'quantity': qty})
            except ValueError:
                # If parsing fails for any part, skip that segment.
                continue
        return items

    def save(self, commit=True):
        """
        Overridden save() method for the NewProjectForm.
        If a FurnitureTemplate is selected and no custom pieces are provided,
        auto-generate the custom_pieces from the template's default string.
        Then, parse the pieces string and create corresponding Piece objects.
        """
        instance = super().save(commit=False)
        template = self.cleaned_data.get('furniture_template')
        custom = self.cleaned_data.get('custom_pieces', '').strip()

        # Use template defaults if provided and custom input is blank.
        if template and not custom:
            custom = template.get_default_pieces()  # Should return a string like "50x30:2, 40x10:3"
        
        if commit:
            # Save the project instance first so we have an ID for related pieces.
            instance.save()
            # Parse the piece string into a list of piece dictionaries.
            piece_data = parse_piece_string(custom)
            # Create Piece objects for each parsed entry.
            for item in piece_data:
                Piece.objects.create(
                    project=instance,
                    width=item['width'],
                    height=item['height'],
                    quantity=item['quantity']
                )
        return instance
