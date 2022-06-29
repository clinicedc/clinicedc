from typing import Any

from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import m2m_changed, post_delete, post_save
from django.dispatch import receiver
from edc_constants.constants import CLOSED, NEW, OPEN
from edc_notification import site_notifications
from simple_history.signals import post_create_historical_record

from ..utils import reset_and_delete_action_item
from .action_item import ActionItem
from .action_model_mixin import ActionModelMixin, ActionNoManagersModelMixin


def update_or_create_action_item(instance: Any, created: bool, using: dict):
    action_item = None
    action_cls = instance.get_action_cls()
    if not instance.action_item:
        action_item = ActionItem.objects.using(using).get(
            action_identifier=instance.action_identifier,
            subject_identifier=instance.subject_identifier,
        )
        instance.action_item = action_item
    # instantiate action class
    action_cls(
        action_item=action_item or instance.action_item,
        subject_identifier=instance.subject_identifier,
        using=using,
    )
    if created and instance.action_item.status == NEW:
        instance.action_item.status = OPEN
        instance.action_item.save(using=using)
    update_action_item_reason(instance)


def update_action_item_reason(instance):
    action_item_reason = instance.get_action_item_reason()
    if action_item_reason:
        instance.action_item_reason = action_item_reason
        instance.save_base(update_fields=["action_item_reason"])


@receiver(m2m_changed, weak=False, dispatch_uid="update_action_item_reason_on_m2m_changed")
def update_action_item_reason_on_m2m_changed(action, instance, **kwargs):
    if "historical" not in instance._meta.label_lower and isinstance(
        instance, (ActionModelMixin, ActionNoManagersModelMixin)
    ):
        update_action_item_reason(instance)


@receiver(m2m_changed, weak=False, dispatch_uid="update_or_create_action_item_on_m2m_change")
def update_or_create_action_item_on_m2m_change(action, instance, using, **kwargs):
    if "historical" not in instance._meta.label_lower and isinstance(
        instance, (ActionModelMixin, ActionNoManagersModelMixin)
    ):
        update_or_create_action_item(instance, False, using)


@receiver(post_save, weak=False, dispatch_uid="update_or_create_action_item_on_post_save")
def update_or_create_action_item_on_post_save(
    sender, instance, raw, created, using, update_fields, **kwargs
):
    """Updates action item for a model using the ActionModelMixin.

    The update is done by instantiating the action class associated
    with this model's instance.
    """
    if not raw and not update_fields:
        try:
            instance.action_name  # noqa
            instance.action_item  # noqa
        except AttributeError as e:
            if "action_name" not in str(e) and "action_item" not in str(e):
                raise
        else:
            if "historical" not in instance._meta.label_lower and isinstance(
                instance, (ActionModelMixin, ActionNoManagersModelMixin)
            ):
                update_or_create_action_item(instance, created, using)


@receiver(post_delete, weak=False, dispatch_uid="action_on_reference_model_post_delete")
def action_on_reference_model_post_delete(sender, instance: Any, using, **kwargs):
    """Re-opens an action item when the action's reference
    model is deleted.

    Also removes any "next" actions.

    Recreates the next action if needed.
    """
    if not isinstance(instance, ActionItem):
        try:
            instance.get_action_cls()
        except AttributeError as e:
            if "get_action_cls" not in str(e):
                raise
        else:
            reset_and_delete_action_item(instance, using)
    elif isinstance(instance, ActionItem):
        if instance.parent_action_item:
            try:
                parent_reference_obj = instance.parent_reference_obj
            except ObjectDoesNotExist:
                pass
            else:
                parent_reference_obj.action_item.action_cls(
                    action_item=instance.parent_reference_obj.action_item,
                    subject_identifier=instance.subject_identifier,
                    using=using,
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
                **kwargs,
            )
            site_notifications.notify(**opts)
