from __future__ import annotations

from typing import TYPE_CHECKING, Type

from django.apps import apps as django_apps
from django.conf import settings

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


def verify_model_cls_registered_with_admin():
    return getattr(settings, "EDC_METADATA_VERIFY_MODELS_REGISTERED_WITH_ADMIN", False)


def refresh_references_and_metadata_for_timepoint(
    appointment_or_related_visit, skip_references: bool | None = None
):
    """Refresh references and metadata for the given timepoint.

    Note: unlike the signal we call `update_references_on_save`
    (note the `s` in `references`) instead.

    See also `metadata_create_on_post_save`, `ReferenceModelMixin`
    and `CreatesMetadataModelMixin`.
    """
    if appointment_or_related_visit:
        try:
            related_visit = appointment_or_related_visit.related_visit
        except AttributeError:
            related_visit = appointment_or_related_visit
        if not skip_references:
            related_visit.update_references_on_save()
        related_visit.metadata_create()
        if django_apps.get_app_config("edc_metadata").metadata_rules_enabled:
            related_visit.run_metadata_rules()
