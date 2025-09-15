from __future__ import annotations

from typing import TYPE_CHECKING

from django import forms
from django.apps import apps as django_apps
from django.conf import settings
from django.contrib.auth import get_permission_codename
from django.contrib.messages import ERROR
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext as _

from edc_model_admin.utils import add_to_messages_once
from edc_utils import convert_php_dateformat

from .constants import TMG_ROLE

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest

    from edc_adverse_event.model_mixins import (
        AeFollowupModelMixin,
        AeInitialModelMixin,
        DeathReportModelMixin,
    )


def validate_ae_initial_outcome_date(form_obj):
    ae_initial = form_obj.cleaned_data.get("ae_initial")
    if not ae_initial and form_obj.instance:
        try:
            ae_initial = form_obj.instance.ae_initial
        except ObjectDoesNotExist:
            pass
    outcome_date = form_obj.cleaned_data.get("outcome_date")
    if ae_initial and outcome_date:
        if outcome_date < ae_initial.ae_start_date:
            formatted_dte = ae_initial.ae_start_date.strftime(
                convert_php_dateformat(settings.SHORT_DATE_FORMAT)
            )
            raise forms.ValidationError(
                {"outcome_date": f"May not be before the AE start date {formatted_dte}."}
            )


def get_adverse_event_admin_site() -> str:
    return getattr(
        settings, "ADVERSE_EVENT_ADMIN_SITE", f"{get_adverse_event_app_label()}_admin"
    )


def get_adverse_event_app_label() -> str:
    app_label = getattr(settings, "ADVERSE_EVENT_APP_LABEL", None)
    if not app_label:
        app_label = getattr(settings, "EDC_ADVERSE_EVENT_APP_LABEL", None)
    if not app_label:
        raise ValueError(
            "Attribute not set. See `get_adverse_event_app_label()` or "
            "`settings.EDC_ADVERSE_EVENT_APP_LABEL`."
        )
    return app_label


def get_hospitalization_model_app_label() -> str:
    return getattr(
        settings,
        "EDC_ADVERSE_EVENT_HOSPITALIZATION_APP_LABEL",
        get_adverse_event_app_label(),
    )


def get_ae_model(
    model_name,
) -> type[DeathReportModelMixin] | type[AeInitialModelMixin] | type[AeFollowupModelMixin]:
    return django_apps.get_model(f"{get_adverse_event_app_label()}.{model_name}")


def get_ae_model_name(model_name: str) -> str:
    return f"{get_adverse_event_app_label()}.{model_name}"


def has_valid_tmg_perms(request: WSGIRequest, add_message: bool = None):
    """Checks if user has TMG_ROLE but not granted add/change
    perms to any non-TMG AE models.

    add_message: if True, adds a message to message context.
    """
    non_tmg_ae_models = ["aeinitial", "aefollowup", "deathreport"]
    # check role
    try:
        has_valid_perms = request.user.userprofile.roles.get(name=TMG_ROLE)
    except ObjectDoesNotExist:
        has_valid_perms = False
        if add_message:
            add_to_messages_once(
                request,
                ERROR,
                (
                    "Access disabled. User has not been granted a TMG role. "
                    "Contact your administrator."
                ),
            )
    # check AE model perms
    if has_valid_tmg_perms:
        codenames = {}
        for model_name in non_tmg_ae_models:
            model_cls = get_ae_model(model_name)
            codename = get_permission_codename("change", model_cls._meta)
            codenames.update({model_cls: f"{model_cls._meta.app_label}.{codename}"})
        for model_cls, codename in codenames.items():
            if request.user.has_perm(codename):
                if add_message:
                    add_to_messages_once(
                        request,
                        ERROR,
                        (
                            _(
                                "Access disabled. A TMG user may not have change "
                                "permission for any adverse event form. Contact your "
                                "administrator. Got %(verbose_name)s"
                            )
                            % {"verbose_name": model_cls._meta.verbose_name}
                        ),
                    )
                has_valid_perms = False
                break
    return has_valid_perms
