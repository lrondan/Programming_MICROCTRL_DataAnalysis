# panel_0/templatetags/dynamic.py
from django import template

register = template.Library()

@register.filter
def getattr_value(obj, attr_name):
    """Devuelve getattr(obj, attr_name, None) si attr_name es string"""
    if isinstance(attr_name, str):
        return getattr(obj, attr_name, None)
    return None