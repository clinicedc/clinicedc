from django.apps import apps as django_apps
from edc_constants.constants import CLOSED, NEW

from edc_action_item.create_or_update_action_type import create_or_update_action_type
from edc_action_item.identifiers import ActionIdentifier
from edc_action_item.models import ActionItem


def update_action_identifier(model=None, action_cls=None, apps=None, status=None):
    apps = apps or django_apps
    action_item_cls = apps.get_model("edc_action_item.actionitem")
    model_cls = apps.get_model(model)
    action_type = create_or_update_action_type(apps=apps, **action_cls.as_dict())
    for obj in model_cls.objects.filter(action_identifier__isnull=True):
        action_item = action_item_cls(
            subject_identifier=obj.subject_visit.subject_identifier,
            action_type=action_type,
            action_identifier=ActionIdentifier().identifier,
        )
        action_item.linked_to_reference = True
        action_item.status = status or CLOSED
        action_item.save()
        obj.action_identifier = action_item.action_identifier
        obj.action_item = action_item
        obj.save_base(update_fields=["action_identifier", "action_item"])


def reset_and_delete_action_item(instance, using=None):
    """Called by signal"""
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
    if action_item.action.delete_with_reference_object:
        action_item.delete()
