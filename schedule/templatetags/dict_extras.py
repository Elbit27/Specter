from django import template

register = template.Library()

@register.filter
def dict_key(d, key):
    """Возвращает значение словаря по ключу"""
    return d.get(key, {})
