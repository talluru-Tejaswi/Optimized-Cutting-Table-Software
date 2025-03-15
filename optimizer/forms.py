from django import forms

class NewProjectForm(forms.Form):
    name = forms.CharField(max_length=100, label="Project Name")
    material_type = forms.ChoiceField(
        choices=[('Wood', 'Wood'), ('Metal', 'Metal'), ('Plastic', 'Plastic')],
        label="Material Type"
    )
    stock_width = forms.FloatField(label="Stock Width (mm)")
    stock_height = forms.FloatField(label="Stock Height (mm)")
