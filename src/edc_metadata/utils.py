from __future__ import annotations

from typing import TYPE_CHECKING, Any, Type

from django.apps import apps as django_apps
from django.conf import settings
from django.db.models import QuerySet

from .constants import CRF, KEYED, REQUISITION

if TYPE_CHECKING:
    from edc_metadata.models import CrfMetadata, RequisitionMetadata


class HasKeyedMetadata(Exception):
    pass


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


def refresh_metadata_for_timepoint(appointment_or_related_visit):
    """Refresh metadata for the given timepoint.

    See also `metadata_create_on_post_save` and `CreatesMetadataModelMixin`.
    """
    if appointment_or_related_visit:
        try:
            related_visit = appointment_or_related_visit.related_visit
        except AttributeError:
            related_visit = appointment_or_related_visit
        related_visit.metadata_create()
        if django_apps.get_app_config("edc_metadata").metadata_rules_enabled:
            related_visit.run_metadata_rules()


def get_crf_metadata(instance: Any) -> QuerySet[CrfMetadata]:
    """Returns a queryset of crf metedata."""
    opts = dict(
        subject_identifier=instance.subject_identifier,
        visit_schedule_name=instance.visit_schedule_name,
        schedule_name=instance.schedule_name,
        visit_code=instance.visit_code,
        visit_code_sequence=instance.visit_code_sequence,
    )
    return get_crf_metadata_model_cls().objects.filter(**opts)


def get_requisition_metadata(instance: Any) -> QuerySet[RequisitionMetadata]:
    """Returns a queryset of requisition metadata"""
    opts = dict(
        subject_identifier=instance.subject_identifier,
        visit_schedule_name=instance.visit_schedule_name,
        schedule_name=instance.schedule_name,
        visit_code=instance.visit_code,
        visit_code_sequence=instance.visit_code_sequence,
    )
    return get_requisition_metadata_model_cls().objects.filter(**opts)


def has_keyed_metadata(appointment, raise_on_true=None) -> bool:
    """Return True if data has been submitted for this timepoint."""
    exists = any(
        [
            get_crf_metadata(appointment).filter(entry_status=KEYED).exists(),
            get_requisition_metadata(appointment).filter(entry_status=KEYED).exists(),
        ]
    )
    if exists and raise_on_true:
        raise HasKeyedMetadata(
            "Metadata data exists for this timepoint. Got "
            f"{appointment.visit_code}.{appointment.visit_code_sequence}."
        )
    return exists
