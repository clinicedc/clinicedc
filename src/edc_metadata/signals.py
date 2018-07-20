from django.apps import apps as django_apps
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


@receiver(post_save, weak=False, dispatch_uid="metadata_create_on_post_save")
def metadata_create_on_post_save(sender, instance, raw, created, using,
                                 update_fields, **kwargs):
    """Creates all meta data on post save of model using
    CreatesMetaDataModelMixin.

    For example, when saving the visit model.
    """
    if not raw:
        try:
            instance.reference_creator_cls(model_obj=instance)
        except AttributeError:
            pass

        try:
            instance.metadata_create()
        except AttributeError as e:
            if 'metadata_create' not in str(e):
                raise
        else:
            if django_apps.get_app_config('edc_metadata_rules').metadata_rules_enabled:
                instance.run_metadata_rules()


@receiver(post_save, weak=False, dispatch_uid="metadata_update_on_post_save")
def metadata_update_on_post_save(sender, instance, raw, created, using,
                                 update_fields, **kwargs):
    """Updates the metadata record on post save of a CRF model.

    Does not create metadata.
    """

    if not raw and not update_fields:
        try:
            instance.reference_updater_cls(model_obj=instance)
        except AttributeError:
            pass

        try:
            instance.metadata_update()
        except AttributeError as e:
            if 'metadata_update' not in str(e):
                raise
        else:
            if django_apps.get_app_config('edc_metadata_rules').metadata_rules_enabled:
                instance.run_metadata_rules_for_crf()


@receiver(post_delete, weak=False, dispatch_uid="metadata_reset_on_post_delete")
def metadata_reset_on_post_delete(sender, instance, using, **kwargs):
    """Deletes a single instance used by UpdatesMetadataMixin.

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
        if 'metadata_reset_on_delete' not in str(e):
            raise
    else:
        if django_apps.get_app_config('edc_metadata_rules').metadata_rules_enabled:
            instance.run_metadata_rules_for_crf()
    # deletes all for a visit used by CreatesMetadataMixin
    try:
        instance.metadata_delete_for_visit()
    except AttributeError as e:
        if 'metadata_delete_for_visit' not in str(e):
            raise
