from django import template

from ..site import sites

register = template.Library()


@register.filter(name="country")
def country(request):
    return sites.get_current_country(request)
