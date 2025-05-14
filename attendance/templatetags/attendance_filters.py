from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return ''
@register.filter
def dict_get(dictionary, key):
    try:
        return dictionary.get(key)
    except AttributeError:
        return None