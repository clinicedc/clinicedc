from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING

from django.core.exceptions import ObjectDoesNotExist

from .reference_range_colllection_model_cls import reference_range_colllection_model_cls

if TYPE_CHECKING:
    from ..models import ReferenceRangeCollection


__all__ = ["get_reference_range_collection"]


def get_reference_range_collection(obj) -> ReferenceRangeCollection:
    """Returns the reference range collection instance"""
    reference_range_collection = None
    if obj:
        try:
            name = obj.requisition.panel_object.reference_range_collection_name
        except AttributeError:
            name = obj.panel_object.reference_range_collection_name
        with contextlib.suppress(ObjectDoesNotExist):
            reference_range_collection = reference_range_colllection_model_cls().objects.get(
                name=name
            )
    return reference_range_collection
