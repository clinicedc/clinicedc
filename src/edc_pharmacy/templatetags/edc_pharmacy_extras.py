from django import template
from django.conf import settings
from edc_dashboard.utils import get_bootstrap_version

register = template.Library()


@register.inclusion_tag(
    f"edc_pharmacy/bootstrap{get_bootstrap_version()}/prescription_item_description.html",
    takes_context=True,
)
def format_prescription_description(context, prescription_item):
    context["SHORT_DATE_FORMAT"] = settings.SHORT_DATE_FORMAT
    context["prescription_item"] = prescription_item
    return context
