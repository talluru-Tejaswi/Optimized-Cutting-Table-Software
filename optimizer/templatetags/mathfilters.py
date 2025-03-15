# optimizer/templatetags/mathfilters.py
from django import template

register = template.Library()

@register.filter
def div(value, arg):
    """Divide value by arg: {{ value|div:arg }}"""
    try:
        return float(value) / float(arg)
    except:
        return value
