# templatetags/form_tags.py

from django import template

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css_class):
    """Agrega una clase CSS a los campos del formulario"""
    try:
        return field.as_widget(attrs={'class': css_class})
    except AttributeError:
        # Si el objeto no tiene 'as_widget', lo devolvemos sin modificar
        return field
