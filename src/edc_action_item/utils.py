from django.apps import apps as django_apps
from edc_constants.constants import CLOSED, NEW
from tqdm import tqdm

from .create_or_update_action_type import create_or_update_action_type
from .identifiers import ActionIdentifier
from .models import ActionItem
from .site_action_items import AlreadyRegistered, site_action_items


def update_action_identifier(model=None, action_cls=None, apps=None, status=None):
    """Update an action_identifier field for an existing model
    recently updated to use an action class.

    For example, in a migration (RunPython):
        def update_followup_examination_action_identifier(apps, schema_editor):
            update_action_identifier(
                    model="meta_subject.followupexamination",
                    action_cls=FollowupExaminationAction,
                    apps=apps,
            )
    """

    apps = apps or django_apps
    action_item_cls = apps.get_model("edc_action_item.actionitem")
    model_cls = apps.get_model(model)
    action_type = create_or_update_action_type(apps=apps, **action_cls.as_dict())
    for obj in tqdm(model_cls.objects.filter(action_identifier__isnull=True)):
        action_item = action_item_cls(
            subject_identifier=obj.related_visit.subject_identifier,
            action_type=action_type,
            action_identifier=ActionIdentifier().identifier,
            site=obj.related_visit.site,
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
        parent_action_item=action_item,
        status=NEW,
    ):
        obj.delete(using=using)
    for obj in ActionItem.objects.using(using).filter(
        related_action_item=action_item,
        status=NEW,
    ):
        obj.delete(using=using)
    if action_item.action.delete_with_reference_object:
        action_item.delete()


def register_actions(*action_cls):
    for cls in action_cls:
        try:
            site_action_items.register(cls)
        except AlreadyRegistered:
            pass
