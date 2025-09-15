from django import template
import hashlib

register = template.Library()

@register.filter
def naira(value):
    try:
        value = float(value)
        return "₦{:,.2f}".format(value)
    except (ValueError, TypeError):
        return value

