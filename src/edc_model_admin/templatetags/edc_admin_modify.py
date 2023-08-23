from __future__ import annotations

from urllib.parse import urlencode
from warnings import warn

from django import template
from django.contrib.admin.templatetags.admin_modify import (
    submit_row as django_submit_row,
)
from django.urls.base import reverse
from django.urls.exceptions import NoReverseMatch
from django_revision.revision import site_revision
from edc_constants.constants import NO, YES
from edc_protocol import Protocol

from edc_model_admin.utils import get_next_url

register = template.Library()


class EdcContextProcessorError(Exception):
    pass


def get_request_object(context):
    """Returns a request object or raises EdcContextProcessorError."""
    request = context.get("request")
    if not request:
        raise EdcContextProcessorError(
            "Request object not found in template context. "
            "Try enabling the context processor "
            "'django.template.context_processors.request'"
        )
    return request


def get_subject_identifier(context):
    """Returns the subject identifier."""
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
    """Returns the url for the Cancel button on the change_form."""
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
                except NoReverseMatch:
                    cancel_url = None
    return cancel_url


@register.inclusion_tag("edc_submit_line.html", takes_context=True)
def edc_submit_row(
    context,
    cancel_url: str | None = None,
    cancel_url_kwargs: dict | None = None,
    cancel_url_querystring_data: dict | None = None,
    show_delete: bool | None = None,
):
    """Returns context to django_submit_row.

    Add to context in add_view or change_view.

    See also ModelAdminRedirectAllToChangelistMixin
    """
    request = get_request_object(context)
    if request:
        if int(request.site.id) == int(context.get("reviewer_site_id", 0)):
            context.update({"save_next": None})
            context.update({"show_delete": None})
    show_save = context.get("show_save")
    if "save_next" in context:
        context["save_next"] = show_save
    if "show_cancel" in context:
        if cancel_url:
            cancel_url = reverse(cancel_url, kwargs=(cancel_url_kwargs or {}))
            if cancel_url_querystring_data:
                cancel_url = f"{cancel_url}?{urlencode(cancel_url_querystring_data)}"
        context["cancel_url"] = cancel_url or get_cancel_url(context)
    if show_delete is False:
        context["show_delete"] = show_delete
    return django_submit_row(context)


@register.inclusion_tag("logout_row.html", takes_context=True)
def logout_row(context):
    return dict(
        user=context.get("request").user,
        request=context.get("request"),
        site_url=context.get("site_url"),
    )


@register.inclusion_tag("edc_revision_line.html", takes_context=True)
def revision_row(context):
    return dict(
        copyright=context.get("copyright") or Protocol().copyright,
        institution=context.get("institution") or Protocol().institution,
        revision=context.get("revision") or site_revision.tag,
        disclaimer=context.get("disclaimer") or Protocol().disclaimer,
    )


@register.inclusion_tag("edc_instructions.html", takes_context=True)
def instructions(context):
    return {"instructions": context.get("instructions")}


@register.inclusion_tag("edc_additional_instructions.html", takes_context=True)
def additional_instructions(context):
    return {
        "additional_instructions": context.get("additional_instructions"),
        "notification_instructions": context.get("notification_instructions"),
    }


@register.filter
def get_label_lower(model) -> str:
    """
    Returns label_lower for a model.
    """
    if model:
        return model._meta.label_lower
    return ""


@register.inclusion_tag("yes_no_coloring.html", takes_context=False)
def yes_no_coloring(value) -> dict:
    context = dict(value=value)
    if value == YES:
        context.update(color="green")
    elif value == NO:
        context.update(color="red")
    return context


@register.inclusion_tag("navbar_for_admin_templates.html", takes_context=True)
def show_navbar_for_admin_templates(context):
    """bootstrap 5"""
    return context


@register.inclusion_tag("navbar_for_admin_templates_b3.html", takes_context=True)
def show_navbar_for_admin_templates_b3(context):
    return context
