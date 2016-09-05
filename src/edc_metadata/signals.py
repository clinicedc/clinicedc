from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


@receiver(post_save, weak=False, dispatch_uid="metadata_create_on_post_save")
def metadata_create_on_post_save(sender, instance, raw, created, using, update_fields, **kwargs):
    """Create all meta data on post save of model using CreatesMetaDataModelMixin.

    For example, when saving the visit model."""
    if not raw:
        try:
            if instance.metadata_create(sender=sender, instance=instance):
                instance.metadata_run_rules()
        except AttributeError as e:
            if 'metadata_create' not in str(e):
                raise AttributeError(e)


@receiver(post_save, weak=False, dispatch_uid="metadata_update_on_post_save")
def metadata_update_on_post_save(sender, instance, raw, created, using, update_fields, **kwargs):
    """Update the meta data record on post save of a model."""

    if not raw:
        try:
            instance.metadata_update()
            instance.visit.metadata_run_rules()
        except AttributeError as e:
            if 'metadata_update' not in str(e):
                raise AttributeError(e)


@receiver(post_delete, weak=False, dispatch_uid="metadata_delete_on_post_save")
def metadata_delete_on_post_save(sender, instance, using, **kwargs):
    try:
        instance.metadata_delete()
        instance.visit.metadata_run_rules()
    except AttributeError as e:
        if 'metadata_delete' not in str(e):
            raise AttributeError(e)
