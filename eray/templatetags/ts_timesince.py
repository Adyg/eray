from django.template import Library, Node, TemplateSyntaxError
register = Library()

@register.filter
def ts_timesince(value, delimiter=None):
    return value.split(delimiter)[0]

ts_timesince.is_safe = True