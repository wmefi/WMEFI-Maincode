from django import template

register = template.Library()

@register.filter
def get_item(d, key):
    """Safely get dict item in templates."""
    if isinstance(d, dict):
        return d.get(key)
    return None
