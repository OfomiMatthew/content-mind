from django import template

register = template.Library()

@register.filter
def pluck(queryset, field_name):
    """
    Extracts a list of attribute values from a queryset.
    Usage: {{ queryset|pluck:"field_name" }}
    """
    return [getattr(obj, field_name) for obj in queryset]
