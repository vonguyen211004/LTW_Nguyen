from django import template
from decimal import Decimal

register = template.Library()

@register.filter
def multiply(value, arg):
    """Nhân value với arg"""
    try:
        return Decimal(str(value)) * Decimal(str(arg))
    except (ValueError, TypeError):
        return 0

@register.filter
def percentage(value, arg=100):
    """Tính phần trăm"""
    try:
        return Decimal(str(value)) * Decimal(str(arg))
    except (ValueError, TypeError):
        return 0