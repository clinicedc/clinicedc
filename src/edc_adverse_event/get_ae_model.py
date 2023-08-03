from __future__ import annotations

from typing import TYPE_CHECKING, Type

from django.apps import apps as django_apps
from django.conf import settings

if TYPE_CHECKING:
    from edc_adverse_event.model_mixins import (
        AeFollowupModelMixin,
        AeInitialModelMixin,
        DeathReportModelMixin,
    )


def get_ae_model(
    model_name,
) -> Type[DeathReportModelMixin] | Type[AeInitialModelMixin] | Type[AeFollowupModelMixin]:
    return django_apps.get_model(f"{settings.ADVERSE_EVENT_APP_LABEL}.{model_name}")


def get_ae_model_name(model_name) -> str:
    return f"{settings.ADVERSE_EVENT_APP_LABEL}.{model_name}"
