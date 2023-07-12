from django.apps import apps as django_apps
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from edc_metadata import KEYED


@receiver(post_save, weak=False, dispatch_uid="metadata_create_on_post_save")
def metadata_create_on_post_save(
    sender, instance, raw, created, using, update_fields, **kwargs
) -> None:
    """Creates all metadata on post save of model using
    CreatesMetaDataModelMixin.

    For example, when saving the visit model.

    See also edc_reference.ReferenceModelMixin and
    RequisitionReferenceModelMixin .
    """
    if (
        not raw
        and not update_fields
        and not hasattr(instance, "metadata_update")
        and not instance._meta.label_lower.split(".")[1].startswith("historical")
    ):
        try:
            # update_reference_on_save (from edc-reference) called here
            # to ensure called before metadata funcs below
            instance.update_reference_on_save()
        except AttributeError as e:
            if "update_reference_on_save" not in str(e):
                raise
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
    """Updates the single metadata record on post save of a CRF model.

    Does not "create" metadata.
    """
    if (
        not raw
        and not update_fields
        and not hasattr(instance, "metadata_create")
        and not instance._meta.label_lower.split(".")[1].startswith("historical")
    ):
        # if not raw and not update_fields:
        try:
            instance.update_reference_on_save()
        except AttributeError as e:
            if "update_reference_on_save" not in str(e):
                raise
        try:
            instance.metadata_update(entry_status=KEYED)
        except AttributeError as e:
            if "metadata_update" not in str(e):
                raise
        else:
            if django_apps.get_app_config("edc_metadata").metadata_rules_enabled:
                instance.run_metadata_rules_for_crf(allow_create=True)


@receiver(post_delete, weak=False, dispatch_uid="metadata_reset_on_post_delete")
def metadata_reset_on_post_delete(sender, instance, using, **kwargs) -> None:
    """Deletes a single model instance used by UpdatesMetadataMixin.

    Not used by CrfMetadata and RequisitionMetadata.

    Calls reference_deleter_cls in case this signal fires before
    the post_delete signal in edc_reference.
    """
    try:
        instance.reference_deleter_cls(model_obj=instance)
    except AttributeError:
        pass

    try:
        instance.metadata_reset_on_delete()
    except AttributeError as e:
        if "metadata_reset_on_delete" not in str(e):
            raise
    else:
        if django_apps.get_app_config("edc_metadata").metadata_rules_enabled:
            instance.run_metadata_rules_for_crf()
    # deletes all for a visit used by CreatesMetadataMixin
    try:
        instance.metadata_delete_for_visit()
    except AttributeError as e:
        if "metadata_delete_for_visit" not in str(e):
            raise
