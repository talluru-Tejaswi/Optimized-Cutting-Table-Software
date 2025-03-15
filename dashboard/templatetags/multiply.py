
# in a custom template filter, e.g. "multiply.py"
from django import template
register = template.Library()

@register.filter
def mul(value, arg):
    try:
        return float(value) * float(arg)
    except:
        return value
