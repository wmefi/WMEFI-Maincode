from django import template

register = template.Library()

@register.filter
def dict_get(d, key):
    try:
        return d.get(key)
    except Exception:
        return ''

@register.filter
def in_list(value, seq):
    try:
        return value in (seq or [])
    except Exception:
        return False
