from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver


@receiver(post_save, weak=False, dispatch_uid="export_to_transaction_on_post_save")
def export_to_transaction_on_post_save(sender, instance, raw, created, using, update_fields, **kwargs):
    """Serializes the model instance to export history model
    if manager exists."""
    if not raw:
        try:
            change_type = 'I' if created else 'U'
            sender.export_history.serialize_to_export_transaction(instance, change_type, using=using)
        except AttributeError as attribute_error:
            if str(attribute_error).endswith("has no attribute 'export_history'"):
                pass
            else:
                raise


@receiver(pre_delete, weak=False, dispatch_uid="export_to_transaction_on_pre_delete")
def export_to_transaction_on_pre_delete(sender, instance, using, **kwargs):
    """Serializes the model instance, before deleting, to export
    history model if manager exists."""
    try:
        sender.export_history.serialize_to_export_transaction(instance, 'D', using=using)
    except AttributeError:
        pass
