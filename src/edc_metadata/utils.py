from __future__ import annotations

from typing import TYPE_CHECKING, Type

from django.apps import apps as django_apps

from .constants import CRF, REQUISITION

if TYPE_CHECKING:
    from edc_metadata.models import CrfMetadata, RequisitionMetadata


def get_crf_metadata_model_cls() -> Type[CrfMetadata]:
    return django_apps.get_model("edc_metadata.crfmetadata")


def get_requisition_metadata_model_cls() -> Type[RequisitionMetadata]:
    return django_apps.get_model("edc_metadata.requisitionmetadata")


def get_metadata_model_cls(
    metadata_category: str,
) -> Type[CrfMetadata] | Type[RequisitionMetadata]:
    if metadata_category == CRF:
        model_cls = get_crf_metadata_model_cls()
    elif metadata_category == REQUISITION:
        model_cls = get_requisition_metadata_model_cls()
    else:
        raise ValueError(f"Invalid metadata category. Got {metadata_category}.")
    return model_cls
