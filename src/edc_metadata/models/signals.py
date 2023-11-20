from django.apps import apps as django_apps
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
            if django_apps.get_app_config("edc_metadata").metadata_rules_enabled:
                instance.run_metadata_rules()


@receiver(post_save, weak=False, dispatch_uid="metadata_update_on_post_save")
def metadata_update_on_post_save(
    sender, instance, raw, created, using, update_fields, **kwargs
) -> None:
    """Updates the single metadata record on post save of a
    CRF/Requisition model.

    Does NOT "create" metadata.

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
            if django_apps.get_app_config("edc_metadata").metadata_rules_enabled:
                instance.run_metadata_rules_for_related_visit(allow_create=True)


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
        if django_apps.get_app_config("edc_metadata").metadata_rules_enabled:
            instance.run_metadata_rules_for_related_visit()

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
    if not raw and not kwargs.get("update_fields"):
        if isinstance(instance, (SingletonCrfModelMixin,)):
            appointment = (
                instance.related_visit.appointment.relative_previous_with_related_visit
            )
            while appointment:
                if appointment.related_visit:
                    refresh_metadata_for_timepoint(appointment.related_visit)
                appointment = appointment.relative_previous_with_related_visit
