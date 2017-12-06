from django.core.exceptions import ObjectDoesNotExist
from edc_constants.constants import CLOSED

from .models import ActionType, ActionItem
from .site_action_items import site_action_items


class InvalidActionType(Exception):
    pass


class ActionItemDoesNotExist(Exception):
    pass


class ActionItemHandlerError(Exception):
    pass


class ModelMissingActionClass(Exception):
    pass


class ActionHandler:

    def __init__(self, model_obj=None):
        site_action_items.populate_action_type()
        try:
            self.action = model_obj.action_cls(
                model_obj=model_obj,
                subject_identifier=model_obj.subject_identifier,
                tracking_identifier=model_obj.tracking_identifier)
        except TypeError:
            raise ModelMissingActionClass(
                f'An action class has not been defined on the model. '
                f'Expected action_cls = <Action Class>. See {repr(model_obj.__class__)}.')

    def create(self):
        """Creates any action items if they do not already exist.
        """
        for action_cls in self.action.get_create_actions():
            action_cls = self.action.__class__ if action_cls == 'self' else action_cls
            action_type = ActionType.objects.get(name=action_cls.name)
            try:
                ActionItem.objects.get(
                    subject_identifier=self.action.subject_identifier,
                    action_type=action_type,
                    reference_identifier=self.action.tracking_identifier)
            except ObjectDoesNotExist:
                ActionItem.objects.create(
                    subject_identifier=self.action.subject_identifier,
                    name=action_type.name,
                    action_type=action_type,
                    reference_model=action_type.model,
                    reference_identifier=self.action.tracking_identifier)

    def create_next(self):
        """Creates any next action items if they do not already exist.
        """
        next_actions = self.action.get_next_actions()
        for action_cls in next_actions:
            action_cls = self.action.__class__ if action_cls == 'self' else action_cls
            action_type = ActionType.objects.get(name=action_cls.name)
            opts = dict(
                subject_identifier=self.action.subject_identifier,
                name=action_type.name,
                action_type=action_type,
                parent_reference_identifier=self.action.tracking_identifier,
                parent_model=self.action.reference_model(),
                parent_action_item=self.action.object,
                reference_model=action_type.model,
                reference_identifier=None)
            try:
                ActionItem.objects.get(**opts)
            except ObjectDoesNotExist:
                ActionItem.objects.create(**opts)

    def close(self):
        if self.action.close_action_item_on_save():
            self.action.object.status = CLOSED
            self.action.object.save(update_fields=['status'])
            self.create_next()
