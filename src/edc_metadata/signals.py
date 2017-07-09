from django.apps import apps as django_apps
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from edc_reference import ReferenceModelDeleter

from .exceptions import CreatesMetadataError


@receiver(post_save, weak=False, dispatch_uid="metadata_create_on_post_save")
def metadata_create_on_post_save(sender, instance, raw, created, using,
                                 update_fields, **kwargs):
    """Create all meta data on post save of model using
    CreatesMetaDataModelMixin.

    For example, when saving the visit model.
    """
    if not raw:
        try:
            if instance.metadata_create(sender=sender, instance=instance):
                if django_apps.get_app_config('edc_metadata').metadata_rules_enabled:
                    instance.run_metadata_rules()
        except AttributeError as e:
            if 'metadata_create' not in str(e):
                raise CreatesMetadataError(f'{sender}. Got \'{e}\'. ') from e


@receiver(post_save, weak=False, dispatch_uid="metadata_update_on_post_save")
def metadata_update_on_post_save(sender, instance, raw, created, using,
                                 update_fields, **kwargs):
    """Update the meta data record on post save of a model.
    """

    if not raw:
        try:
            instance.metadata_update()
            if django_apps.get_app_config('edc_metadata').metadata_rules_enabled:
                instance.visit.run_metadata_rules()
        except AttributeError as e:
            if 'metadata_update' not in str(e):
                raise AttributeError(e) from e


@receiver(post_delete, weak=False, dispatch_uid="metadata_reset_on_post_delete")
def metadata_reset_on_post_delete(sender, instance, using, **kwargs):
    # deletes a single instance used by UpdatesMetadataMixin
    ReferenceModelDeleter(model_obj=instance)
    try:
        instance.metadata_reset_on_delete()
        if django_apps.get_app_config('edc_metadata').metadata_rules_enabled:
            instance.visit.run_metadata_rules()
    except AttributeError as e:
        if 'metadata_reset_on_delete' not in str(e):
            raise AttributeError(e) from e
    # deletes all for a visit used by CreatesMetadataMixin
    try:
        instance.metadata_delete_for_visit(instance)
    except AttributeError as e:
        if 'metadata_delete_for_visit' not in str(e):
            raise AttributeError(e) from e
