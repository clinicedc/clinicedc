from __future__ import annotations

from typing import TYPE_CHECKING, Type

from django.apps import apps as django_apps

if TYPE_CHECKING:
    from ..models import GradingData

__all__ = ["grading_data_model_cls"]


def grading_data_model_cls() -> Type[GradingData]:
    return django_apps.get_model("edc_reportable.gradingdata")
