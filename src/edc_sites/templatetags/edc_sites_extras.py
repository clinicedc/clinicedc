from django import template

from edc_sites import get_current_country

register = template.Library()


@register.filter(name="country")
def country(request):
    return get_current_country(request=request)
