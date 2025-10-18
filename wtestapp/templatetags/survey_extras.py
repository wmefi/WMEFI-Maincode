from django import template
import re

register = template.Library()

@register.filter
def get_item(d, key):
    """Safely get dict item in templates."""
    if isinstance(d, dict):
        return d.get(key)
    return None

@register.filter
def extract_followup(answer_text):
    """Extract follow-up text from 'Yes - followup' format"""
    if answer_text and ' - ' in str(answer_text):
        parts = str(answer_text).split(' - ', 1)
        if len(parts) > 1:
            return parts[1]
    return ''

@register.filter
def starts_with_yes(answer_text):
    """Check if answer starts with 'Yes'"""
    if answer_text:
        return str(answer_text).strip().startswith('Yes')
    return False

@register.filter
def remove_trailing_numbers(title):
    """Remove trailing numbers in parentheses from survey title like (13), (4), etc."""
    if title:
        # Remove pattern like " (13)" or " (4)" from the end
        return re.sub(r'\s*\(\d+\)\s*$', '', str(title)).strip()
    return title
