from __future__ import annotations

from typing import TYPE_CHECKING, Type

from django.apps import apps as django_apps

if TYPE_CHECKING:
    from ..models import ReferenceRangeCollection


__all__ = ["reference_range_colllection_model_cls"]


def reference_range_colllection_model_cls() -> Type[ReferenceRangeCollection]:
    return django_apps.get_model("edc_reportable.referencerangecollection")
