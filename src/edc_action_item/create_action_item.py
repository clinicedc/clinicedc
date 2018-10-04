from django.core.exceptions import ObjectDoesNotExist

from .get_action_type import get_action_type


class SingletonActionItemError(Exception):
    pass


class CreateActionItemError(Exception):
    pass


def create_action_item(action_cls, subject_identifier=None,
                       action_identifier=None,
                       related_action_identifier=None,
                       parent_action_identifier=None):
    action_item = None
    if action_cls.singleton:
        try:
            action_item = action_cls.action_item_model_cls().objects.get(
                action_type=get_action_type(action_cls),
                subject_identifier=subject_identifier)
        except ObjectDoesNotExist:
            pass
        else:
            raise SingletonActionItemError(
                f'Action {action_cls.name} can only be '
                f'created once per subject. Got {subject_identifier}.')
    if not action_item:
        opts = {}
        try:
            parent_action_item = action_cls.action_item_model_cls().objects.get(
                action_identifier=parent_action_identifier)
        except ObjectDoesNotExist:
            pass
        else:
            opts.update(
                # parent_action_item=parent_action_item,
                parent_action_identifier=parent_action_item.action_identifier,
                parent_reference_model=parent_action_item.reference_model)
        try:
            related_action_item = action_cls.action_item_model_cls().objects.get(
                action_identifier=related_action_identifier)
        except ObjectDoesNotExist:
            pass
        else:
            opts.update(
                related_action_identifier=related_action_item.action_identifier,
                related_reference_model=related_action_item.reference_model)
        action_item = action_cls.action_item_model_cls()(
            subject_identifier=subject_identifier,
            action_type=get_action_type(action_cls),
            action_identifier=action_identifier,
            linked_to_reference=True, **opts)
        action_item.save()
    return action_item
