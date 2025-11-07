# panel_0/templatetags/utils.py
from django import template

register = template.Library()

@register.filter
def getattr_value(obj, attr_name):
    """Permite usar getattr en templates: {{ d|getattr_value:"valor1" }}"""
    return getattr(obj, attr_name, None)