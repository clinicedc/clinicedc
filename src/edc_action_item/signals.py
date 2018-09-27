from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from edc_constants.constants import NEW

from .models import ActionItem
from .send_email import send_email


@receiver(post_save, weak=False, dispatch_uid='update_or_create_action_item_on_post_save')
def update_or_create_action_item_on_post_save(sender, instance, raw,
                                              created, update_fields, **kwargs):
    """Updates action item for a model using the ActionModelMixin.

    Instantiates the action class on the model with the model's
    instance.
    """
    if not raw and not update_fields:
        try:
            instance.action_identifier
        except AttributeError:
            pass
        else:
            if 'historical' not in instance._meta.label_lower:
                if not isinstance(instance, ActionItem):
                    instance.action_cls()(
                        action_identifier=instance.action_identifier)
                    send_email(instance.action_item)


@receiver(post_save, weak=False, dispatch_uid='send_email_on_new_action_item_post_save')
def send_email_on_new_action_item_post_save(sender, instance, raw,
                                            created, update_fields, **kwargs):
    if not raw and not update_fields:
        try:
            emailed = instance.emailed
        except AttributeError:
            pass
        else:
            if not emailed and isinstance(instance, ActionItem):
                send_email(instance)


@receiver(post_delete, weak=False,
          dispatch_uid="action_on_post_delete")
def action_on_post_delete(sender, instance, using, **kwargs):
    """Re-opens an action item when the action's reference
    model is deleted.
    """
    if not isinstance(instance, ActionItem):
        try:
            instance.action_cls()
        except AttributeError:
            pass
        else:
            obj = ActionItem.objects.get(
                action_identifier=instance.action_identifier)
            obj.status = NEW
            obj.linked_to_reference = False
            obj.save()
