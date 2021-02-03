import os
from textwrap import wrap

import arrow
from django import template
from django.conf import settings
from django.template.loader import select_template
from django.utils.safestring import mark_safe
from edc_constants.constants import OTHER, YES

register = template.Library()


def select_ae_template(relative_path):
    """Returns a template object."""
    local_path = f"{settings.ADVERSE_EVENT_APP_LABEL}/bootstrap{settings.EDC_BOOTSTRAP}/"
    default_path = f"edc_adverse_event/bootstrap{settings.EDC_BOOTSTRAP}/"
    return select_template(
        [
            os.path.join(local_path, relative_path),
            os.path.join(default_path, relative_path),
        ]
    )


def select_description_template(model):
    """Returns a template name."""
    return select_ae_template(f"{model}_description.html").template.name


@register.inclusion_tag(
    f"edc_adverse_event/bootstrap{settings.EDC_BOOTSTRAP}/"
    f"tmg/tmg_ae_listboard_result.html",
    takes_context=True,
)
def tmg_listboard_results(context, results, empty_message=None):
    context["results"] = results
    context["empty_message"] = empty_message
    return context


@register.inclusion_tag(select_description_template("aeinitial"), takes_context=True)
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


@register.inclusion_tag(select_description_template("aefollowup"), takes_context=True)
def format_ae_followup_description(context, ae_followup, wrap_length):
    context["utc_date"] = arrow.now().date()
    context["SHORT_DATE_FORMAT"] = settings.SHORT_DATE_FORMAT
    context["OTHER"] = OTHER
    context["YES"] = YES
    context["ae_followup"] = ae_followup
    context["ae_initial"] = ae_followup.ae_initial
    context["sae_reason"] = mark_safe(
        "<BR>".join(wrap(ae_followup.ae_initial.sae_reason.name, wrap_length or 35))
    )
    context["relevant_history"] = mark_safe(
        "<BR>".join(wrap(ae_followup.relevant_history, wrap_length or 35))
    )
    context["ae_description"] = mark_safe(
        "<BR>".join(wrap(ae_followup.ae_initial.ae_description, wrap_length or 35))
    )
    return context


@register.inclusion_tag(select_description_template("aesusar"), takes_context=True)
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
