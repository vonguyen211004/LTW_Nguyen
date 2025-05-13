from django import template
from decimal import Decimal

register = template.Library()

@register.filter
def format_currency(value):
    """Định dạng số tiền"""
    try:
        return "{:,.0f}".format(value)
    except (ValueError, TypeError):
        return value

@register.filter
def calculate_age(date_of_birth):
    """Tính tuổi từ ngày sinh"""
    from datetime import date
    today = date.today()
    return today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))