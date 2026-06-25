from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from edc_crf.model_mixins import SingletonCrfModelMixin
from edc_metadata import KEYED
from edc_metadata.utils import refresh_metadata_for_timepoint


@receiver(post_save, weak=False, dispatch_uid="metadata_create_on_post_save")
def metadata_create_on_post_save(
    sender, instance, raw, created, using, update_fields, **kwargs
) -> None:
    """Creates all metadata on post save of model using
    CreatesMetaDataModelMixin.

    For example, when saving the related_visit model.

    A related_visit model instance will:
      * delete and re-create ALL metadata for the timepoint
        (`metadata_create`)
      * run ALL metadata rules for the timepoint
        (`run_metadata_rules_for_related_visit`).
    """
    if (
        not raw
        and not update_fields
        and not hasattr(instance, "metadata_update")
        and not instance._meta.label_lower.split(".")[1].startswith("historical")
    ):
        try:
            instance.metadata_create()
        except AttributeError as e:
            if "metadata_create" not in str(e):
                raise
        else:
            refresh_metadata_for_timepoint(instance, allow_create=True)


@receiver(post_save, weak=False, dispatch_uid="metadata_update_on_post_save")
def metadata_update_on_post_save(
    sender, instance, raw, created, using, update_fields, **kwargs
) -> None:
    """Updates the single metadata record on post save of a
    CRF/Requisition model.

    A CRF/Requisition model instance will:
      * update it`s own references (`update_reference_on_save`)
      * update it`s own metadata (`metadata_update`)
      * run ALL metadata rules for the timepoint
        (`run_metadata_rules_for_related_visit`).
    """
    if (
        not raw
        and not update_fields
        and not hasattr(instance, "metadata_create")
        and not instance._meta.label_lower.split(".")[1].startswith("historical")
    ):
        try:
            instance.metadata_update(entry_status=KEYED)
        except AttributeError as e:
            if "metadata_update" not in str(e):
                raise
        else:
            refresh_metadata_for_timepoint(instance, allow_create=True)


@receiver(post_save, weak=False, dispatch_uid="delete_unavailable_on_keyed_post_save")
def delete_unavailable_on_keyed_post_save(
    sender, instance, raw, update_fields, **kwargs
) -> None:
    """When a CRF/Requisition is saved (keyed), remove any matching
    'data unavailable' flag — the data has now been obtained.

    Fires on the source CRF/Requisition save (a user-driven,
    low-frequency event), not on CrfMetadata saves (which happen in
    bulk on regeneration).

    See also `ReviewOutstandingFlaggedView`.
    """
    if (
        raw
        or update_fields
        or hasattr(instance, "metadata_create")  # the related_visit model
        or not hasattr(instance, "metadata_update")  # not a CRF/Requisition
        or instance._meta.label_lower.split(".")[1].startswith("historical")
    ):
        return
    from edc_metadata.constants import CRF  # noqa: PLC0415
    from edc_metadata.models import (  # noqa: PLC0415
        CrfMetadataUnavailable,
        RequisitionMetadataUnavailable,
    )

    try:
        opts = dict(instance.metadata_query_options)
    except (AttributeError, ObjectDoesNotExist):
        return
    opts.pop("timepoint", None)  # not a field on the *Unavailable models
    unavailable_cls = (
        CrfMetadataUnavailable
        if getattr(instance, "metadata_category", None) == CRF
        else RequisitionMetadataUnavailable
    )
    unavailable_cls.objects.filter(**opts).delete()


@receiver(post_delete, weak=False, dispatch_uid="metadata_reset_on_post_delete")
def metadata_reset_on_post_delete(sender, instance, using, **kwargs) -> None:
    """Deletes a single model instance used by UpdatesMetadataMixin.

    Not used by CrfMetadata and RequisitionMetadata.
    """
    try:
        instance.metadata_reset_on_delete()
    except AttributeError as e:
        if "metadata_reset_on_delete" not in str(e):
            raise
    else:
        refresh_metadata_for_timepoint(instance, allow_create=True)

    # deletes all for a visit used by CreatesMetadataMixin
    try:
        instance.metadata_delete_for_visit()
    except AttributeError as e:
        if "metadata_delete_for_visit" not in str(e):
            raise


@receiver(
    post_save,
    weak=False,
    dispatch_uid="metadata_update_previous_timepoints_for_singleton_on_post_save",
)
def metadata_update_previous_timepoints_for_singleton_on_post_save(
    sender, instance, raw, created, using, **kwargs
):
    if (
        not raw
        and not kwargs.get("update_fields")
        and isinstance(instance, (SingletonCrfModelMixin,))
    ):
        appointment = instance.related_visit.appointment.relative_previous_with_related_visit
        while appointment:
            if appointment.related_visit:
                refresh_metadata_for_timepoint(appointment.related_visit, allow_create=False)
            appointment = appointment.relative_previous_with_related_visit
