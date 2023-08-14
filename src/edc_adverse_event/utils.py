from __future__ import annotations

from typing import TYPE_CHECKING, Type

from django import forms
from django.apps import apps as django_apps
from django.conf import settings
from edc_utils import convert_php_dateformat

if TYPE_CHECKING:
    from edc_adverse_event.model_mixins import (
        AeFollowupModelMixin,
        AeInitialModelMixin,
        DeathReportModelMixin,
    )


def validate_ae_initial_outcome_date(form_obj):
    ae_initial = form_obj.cleaned_data.get("ae_initial")
    if not ae_initial and form_obj.instance:
        ae_initial = form_obj.instance.ae_initial
    outcome_date = form_obj.cleaned_data.get("outcome_date")
    if ae_initial and outcome_date:
        if outcome_date < ae_initial.ae_start_date:
            formatted_dte = ae_initial.ae_start_date.strftime(
                convert_php_dateformat(settings.SHORT_DATE_FORMAT)
            )
            raise forms.ValidationError(
                {"outcome_date": f"May not be before the AE start date {formatted_dte}."}
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
        settings, "EDC_ADVERSE_EVENT_HOSPITALIZATION_APP_LABEL", get_adverse_event_app_label()
    )


def get_ae_model(
    model_name,
) -> Type[DeathReportModelMixin] | Type[AeInitialModelMixin] | Type[AeFollowupModelMixin]:
    return django_apps.get_model(f"{get_adverse_event_app_label()}.{model_name}")


def get_ae_model_name(model_name) -> str:
    return f"{get_adverse_event_app_label()}.{model_name}"
