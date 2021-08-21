import yaml
from django import template

register = template.Library()


@register.filter(name="indent")
def indent(value, arg):
    if isinstance(value, dict):
        value = yaml.dump(value)
    return "\n".join([(" "*arg) + line for line in iter(value.splitlines())])
