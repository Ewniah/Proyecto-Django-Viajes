from django import template

register = template.Library()

@register.filter(name='punto_mil')
def punto_mil(value):
    try:
        number = int(value)
        return f"{number:,}".replace(",", ".")
    except (ValueError, TypeError):
        return value