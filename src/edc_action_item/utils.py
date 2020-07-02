from django.apps import apps as django_apps
from edc_action_item.create_or_update_action_type import create_or_update_action_type
from edc_action_item.identifiers import ActionIdentifier
from edc_constants.constants import CLOSED


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
