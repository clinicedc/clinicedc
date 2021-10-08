from django import template
from django.conf import settings

register = template.Library()


@register.inclusion_tag(
    f"edc_pharmacy/bootstrap{settings.EDC_BOOTSTRAP}/prescription_item_description.html",
    takes_context=True,
)
def format_prescription_description(context, prescription_item):
    context["SHORT_DATE_FORMAT"] = settings.SHORT_DATE_FORMAT
    context["prescription_item"] = prescription_item
    return context
