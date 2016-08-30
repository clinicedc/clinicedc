from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver


@receiver(post_save, weak=False, dispatch_uid="metadata_create_on_post_save")
def metadata_create_on_post_save(sender, instance, raw, created, using, update_fields, **kwargs):
    """Create all meta data on post save of model using CreatesMetaDataModelMixin."""
    if not raw:
        try:
            instance.metadata_create()
        except AttributeError as e:
            if 'metadata_create' not in str(e):
                raise


@receiver(post_save, weak=False, dispatch_uid="metadata_update_on_post_save")
def metadata_update_on_post_save(sender, instance, raw, created, using, update_fields, **kwargs):
    """Update a meta data record on post save of the model using the metadata_manager method."""

    if not raw:
        try:
            instance.metadata_update()
        except AttributeError as e:
            if 'metadata_update' not in str(e):
                raise


@receiver(pre_delete, weak=False, dispatch_uid="metadata_delete_on_post_save")
def metadata_delete_on_post_save(sender, instance, using, **kwargs):
    try:
        instance.metadata_delete()
    except AttributeError as e:
        if 'metadata_delete' not in str(e):
            raise
