from django import template
from django.contrib.admin.templatetags.admin_modify import (
    submit_row as django_submit_row,
)
from django.urls.base import reverse
from django.urls.exceptions import NoReverseMatch
from edc_model_admin import get_next_url
from warnings import warn

register = template.Library()


class EdcContextProcessorError(Exception):
    pass


def get_request_object(context):
    """Returns a request object or raises EdcContextProcessorError.
    """
    request = context.get("request")
    if not request:
        raise EdcContextProcessorError(
            "Request object not found in template context. "
            "Try enabling the context processor "
            "'django.template.context_processors.request'"
        )
    return request


def get_subject_identifier(context):
    """Returns the subject identifier.
    """
    request = get_request_object(context)
    subject_identifier = request.GET.get("subject_identifier")
    if not subject_identifier:
        try:
            subject_identifier = context["subject_identifier"]
        except KeyError:
            try:
                subject_identifier = context["original"].subject_identifier
            except (KeyError, AttributeError):
                subject_identifier = None
    return subject_identifier


def get_cancel_url(context, cancel_attr=None):
    """Returns the url for the Cancel button on the change_form.
    """
    request = get_request_object(context)
    cancel_url = request.GET.dict().get("cancel_url")
    if not cancel_url:
        cancel_querystring = request.GET.dict().get(cancel_attr or "cancel")
        if cancel_querystring:
            url = None
            kwargs = {}
            for pos, value in enumerate(cancel_querystring.split(",")):
                if pos == 0:
                    url = value
                else:
                    kwargs.update({value: request.GET.get(value)})
            try:
                cancel_url = reverse(url, kwargs=kwargs)
            except NoReverseMatch as e:
                warn(f"{e}. Got {cancel_url}.")
        else:
            cancel_url = get_next_url(request, warn_to_console=False)
            if not cancel_url:
                url = context["subject_dashboard_url"]
                kwargs = {"subject_identifier": get_subject_identifier(context)}
                try:
                    cancel_url = reverse(url, kwargs=kwargs)
                except NoReverseMatch as e:
                    cancel_url = None
                    warn(f"{str(e)} kwargs={kwargs}. See 'get_cancel_url'.")
    return cancel_url


@register.inclusion_tag("edc_submit_line.html", takes_context=True)
def edc_submit_row(context):

    request = get_request_object(context)
    if request:
        if int(request.site.id) == int(context.get("reviewer_site_id", 0)):
            context.update({"save_next": None})
            context.update({"show_delete": None})

    show_save = context.get("show_save")
    if "save_next" in context:
        context["save_next"] = show_save

    if "show_cancel" in context:
        context["cancel_url"] = get_cancel_url(context)

    return django_submit_row(context)


@register.inclusion_tag("edc_revision_line.html", takes_context=True)
def revision_row(context):
    return dict(
        copyright=context.get("copyright"),
        institution=context.get("institution"),
        revision=context.get("revision"),
        disclaimer=context.get("disclaimer"),
    )


@register.inclusion_tag("edc_instructions.html", takes_context=True)
def instructions(context):
    instructions = context.get("instructions")
    return {"instructions": instructions}


@register.inclusion_tag("edc_additional_instructions.html", takes_context=True)
def additional_instructions(context):
    additional_instructions = context.get("additional_instructions")
    notification_instructions = context.get("notification_instructions")
    return {
        "additional_instructions": additional_instructions,
        "notification_instructions": notification_instructions,
    }
