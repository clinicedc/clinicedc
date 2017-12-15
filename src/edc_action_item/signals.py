from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import ActionItem, ActionItemUpdate
from .reference_model_updater import ReferenceModelUpdater


@receiver(post_save, weak=False, sender=ActionItem, dispatch_uid='action_item_on_post_save')
def action_item_on_post_save(sender, instance, raw, created, update_fields, **kwargs):
    """Updates the reference model instance with the action_identifier,
    if this is an action type connected to a model.
    """
    if not raw and not update_fields:
        if instance.reference_model:
            updater = ReferenceModelUpdater(action_item=instance)
            updater.update()


@receiver(post_save, weak=False, dispatch_uid='update_or_create_action_item_on_post_save')
def update_action_item_on_post_save(sender, instance, raw,
                                    created, update_fields, **kwargs):
    """Updates action item for a model using the ActionItemModelMixin.
    """
    if not raw and not update_fields:
        try:
            instance.action_identifier
        except AttributeError:
            pass
        else:
            if ('historical' not in instance._meta.label_lower
                    and not isinstance(instance, (ActionItem, ActionItemUpdate))):
                instance.action_cls(model_obj=instance)
