from __future__ import annotations

from typing import TYPE_CHECKING

from django.apps import apps as django_apps

if TYPE_CHECKING:
    from ..models import NormalData


__all__ = ["normal_data_model_cls"]


def normal_data_model_cls() -> type[NormalData]:
    return django_apps.get_model("edc_reportable.normaldata")
