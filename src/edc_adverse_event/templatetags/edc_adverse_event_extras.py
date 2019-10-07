import arrow

from django import template
from django.conf import settings
from django.utils.safestring import mark_safe
from edc_constants.constants import OTHER, YES
from textwrap import wrap

register = template.Library()

format_ae_description_template_name = (
    f"edc_adverse_event/bootstrap{settings.EDC_BOOTSTRAP}/"
    "ae_initial_description.html"
)

format_ae_susar_description_template_name = (
    f"edc_adverse_event/bootstrap{settings.EDC_BOOTSTRAP}/" "ae_susar_description.html"
)


@register.inclusion_tag(
    f"edc_adverse_event/bootstrap{settings.EDC_BOOTSTRAP}/"
    f"tmg/ae_listboard_result.html",
    takes_context=True,
)
def tmg_listboard_results(context, results, empty_message=None):
    context["results"] = results
    context["empty_message"] = empty_message
    return context


@register.inclusion_tag(format_ae_description_template_name, takes_context=True)
def format_ae_description(context, ae_initial, wrap_length):
    context["utc_date"] = arrow.now().date()
    context["SHORT_DATE_FORMAT"] = settings.SHORT_DATE_FORMAT
    context["OTHER"] = OTHER
    context["YES"] = YES
    context["ae_initial"] = ae_initial
    context["sae_reason"] = mark_safe(
        "<BR>".join(wrap(ae_initial.sae_reason.name, wrap_length or 35))
    )
    context["ae_description"] = mark_safe(
        "<BR>".join(wrap(ae_initial.ae_description, wrap_length or 35))
    )
    return context


@register.inclusion_tag(format_ae_susar_description_template_name, takes_context=True)
def format_ae_susar_description(context, ae_susar, wrap_length):
    context["utc_date"] = arrow.now().date()
    context["SHORT_DATE_FORMAT"] = settings.SHORT_DATE_FORMAT
    context["OTHER"] = OTHER
    context["YES"] = YES
    context["ae_susar"] = ae_susar
    context["ae_initial"] = ae_susar.ae_initial
    context["sae_reason"] = mark_safe(
        "<BR>".join(wrap(ae_susar.ae_initial.sae_reason.name, wrap_length or 35))
    )
    context["ae_description"] = mark_safe(
        "<BR>".join(wrap(ae_susar.ae_initial.ae_description, wrap_length or 35))
    )
    return context
