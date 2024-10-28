# inventory/templatetags/custom_tags.py

from django import template
from inventory.models import Income, Outcome

register = template.Library()

@register.filter
def is_instance(value, class_name):
    if class_name == "Income":
        return isinstance(value, Income)
    elif class_name == "Outcome":
        return isinstance(value, Outcome)
    return False
