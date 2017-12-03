from django.core.exceptions import ObjectDoesNotExist
from edc_constants.constants import CLOSED

from .models import ActionType, ActionItem


class InvalidActionType(Exception):
    pass


class ActionItemDoesNotExist(Exception):
    pass


class ActionItemHandler:

    def __init__(self, model_obj=None, model_cls=None):
        self.model_obj = model_obj
        self.model_cls = model_cls
        self.reference_model = model_obj._meta.label_lower

    def close(self):
        if self.model_obj.close_action_item_on_save():
            self.model_obj = self.model_cls.objects.get(pk=self.model_obj.pk)
            try:
                action_item = ActionItem.objects.get(
                    reference_identifier=self.model_obj.tracking_identifier,
                    reference_model=self.model_obj._meta.label_lower)
            except ObjectDoesNotExist:
                raise ActionItemDoesNotExist(
                    f'Action item for {self.model_cls} does not exist or has '
                    f'not been created. Either configure this model or '
                    f'another to create the action item or create it manually. '
                    f'(It may also be that you are entering data out of the '
                    f'expected order.)')
            else:
                action_item.status = CLOSED
                action_item.save(update_fields=['status'])
                self.create_next(next_action_type=action_item.next_action_type)

    def create(self):
        """Creates any action items if they do not already exist.
        """
        for action_type_name in self.model_obj.creates_action_items():
            action_type = ActionType.objects.get(name=action_type_name)
            try:
                ActionItem.objects.get(
                    subject_identifier=self.model_obj.subject_identifier,
                    action_type=action_type,
                    reference_identifier=self.model_obj.tracking_identifier)
            except ObjectDoesNotExist:
                opts = {}
                status = CLOSED if self.model_obj.close_action_item_on_save() else None
                if status:
                    opts.update(status=status)
                ActionItem.objects.create(
                    subject_identifier=self.model_obj.subject_identifier,
                    name=action_type.name,
                    action_type=action_type,
                    reference_model=action_type.model,
                    reference_identifier=self.model_obj.tracking_identifier,
                    **opts)

    def create_next(self, next_action_type=None):
        """Creates any next action items if they do not already exist.
        """
        try:
            next_action_type_name = next_action_type.name
        except AttributeError:
            next_action_type_name = None
        for action_type_name in self.model_obj.create_next_action_items(
                action_type_name=next_action_type_name):
            try:
                action_type = ActionType.objects.get(name=action_type_name)
            except ObjectDoesNotExist:
                action_type_names = [
                    obj.name for obj in ActionType.objects.all()]
                raise InvalidActionType(
                    f'Invalid action type when creating next action. '
                    f'Model={self.model_cls}. Expected one of {action_type_names}. '
                    f'Got next_action_type=\'{action_type_name}\'.')
            opts = dict(
                subject_identifier=self.model_obj.subject_identifier,
                name=action_type.name,
                action_type=action_type,
                parent_reference_identifier=self.model_obj.tracking_identifier,
                parent_model=self.model_obj._meta.label_lower,
                reference_model=action_type.model,
                reference_identifier=None)
            try:
                ActionItem.objects.get(**opts)
            except ObjectDoesNotExist:
                ActionItem.objects.create(**opts)
