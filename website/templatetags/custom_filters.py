# custom_filters.py

from django import template

register = template.Library()

@register.filter(name='replace_comma')
def replace_comma(value):
    return str(value).replace(',', '.')