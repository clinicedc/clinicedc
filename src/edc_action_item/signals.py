from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from edc_constants.constants import NEW, OPEN, CLOSED
from edc_notification import site_notifications
from simple_history.signals import post_create_historical_record

from .models import ActionItem, ActionModelMixin
from .site_action_items import site_action_items


@receiver(
    post_save, weak=False, dispatch_uid="update_or_create_action_item_on_post_save"
)
def update_or_create_action_item_on_post_save(
    sender, instance, raw, created, using, update_fields, **kwargs
):
    """Updates action item for a model using the ActionModelMixin.

    The update is done by instantiating the action class associated
    with this model's instance.
    """
    if not raw and not update_fields:
        try:
            instance.action_name
            instance.action_item
        except AttributeError:
            pass
        else:
            if "historical" not in instance._meta.label_lower and isinstance(
                instance, ActionModelMixin
            ):
                action_item = None
                action_cls = site_action_items.get(instance.action_name)
                if not instance.action_item:
                    action_item = ActionItem.objects.using(using).get(
                        action_identifier=instance.action_identifier
                    )
                    instance.action_item = action_item
                # instantiate action class
                action_cls(action_item=action_item or instance.action_item, using=using)
                if created and instance.action_item.status == NEW:
                    instance.action_item.status = OPEN
                    instance.action_item.save(using=using)


@receiver(post_delete, weak=False, dispatch_uid="action_on_post_delete")
def action_on_post_delete(sender, instance, using, **kwargs):
    """Re-opens an action item when the action's reference
    model is deleted.

    Also removes any "next" actions.

    Recreates the next action if needed.
    """
    if not isinstance(instance, ActionItem):
        try:
            instance.get_action_cls()
        except AttributeError:
            pass
        else:
            action_item = ActionItem.objects.using(using).get(
                action_identifier=instance.action_identifier
            )
            action_item.status = NEW
            action_item.linked_to_reference = False
            action_item.save(using=using)
            for obj in ActionItem.objects.using(using).filter(
                parent_action_item=instance.action_item, status=NEW
            ):
                obj.delete(using=using)
            for obj in ActionItem.objects.using(using).filter(
                related_action_item=instance.action_item, status=NEW
            ):
                obj.delete(using=using)
    elif isinstance(instance, ActionItem):
        if instance.parent_action_item:
            try:
                instance.parent_reference_obj
            except ObjectDoesNotExist:
                pass
            else:
                instance.parent_reference_obj.action_item.action_cls(
                    action_item=instance.parent_reference_obj.action_item, using=using
                ).create_next_action_items()


@receiver(
    post_create_historical_record,
    weak=False,
    dispatch_uid="action_item_notification_on_post_create_historical_record",
)
def action_item_notification_on_post_create_historical_record(
    sender, instance, history_date, history_user, history_change_reason, **kwargs
):
    """Checks and processes any notifications for this model.

    Note, this is the post_create of the historical model.
    """
    if (
        site_notifications.loaded
        and instance._meta.label_lower == "edc_action_item.actionitem"
    ):
        if instance.status != CLOSED:
            opts = dict(
                instance=instance,
                user=instance.user_modified or instance.user_created,
                history_date=history_date,
                history_user=history_user,
                history_change_reason=history_change_reason,
                fail_silently=True,
                **kwargs
            )
            site_notifications.notify(**opts)
