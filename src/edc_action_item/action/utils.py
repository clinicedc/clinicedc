from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from edc_constants.constants import NEW
from pprint import pprint


class SingletonActionItemError(Exception):
    pass


class ActionItemDeleteError(Exception):
    pass


# def create_action_item(action_cls=None, subject_identifier=None,
#                        tracking_identifier=None,
#                        action_item_model_cls=None,
#                        action_type=None,
#                        singleton=None,
#                        instructions=None):
#     """Returns an action item.
#     """
#     def create():
#         return action_item_model_cls.objects.create(
#             subject_identifier=subject_identifier,
#             action_type=action_type,
#             reference_identifier=tracking_identifier,
#             instructions=instructions)
#     if action_cls:
#         action_item_model_cls = action_cls.action_item_model_cls()
#         action_type = action_cls.action_type()
#         singleton = action_cls.singleton
#         instructions = action_cls.instructions
#     try:
#         obj = action_item_model_cls.objects.get(
#             subject_identifier=subject_identifier,
#             action_type=action_type)
#     except ObjectDoesNotExist:
#         obj = create()
#     else:
#         if singleton:
#             raise SingletonActionItemError(
#                 f'Unable to create action item. '
#                 f'{repr(action_cls)} is a singleton class.')
#         else:
#             obj = create()
#
#     return obj


def delete_action_item(action_cls=None, subject_identifier=None):
    """Deletes any NEW action items for a given class
    and subject_identifier.
    """
    try:
        obj = action_cls.action_item_model_cls().objects.get(
            subject_identifier=subject_identifier,
            action_type=action_cls.action_type(),
            status=NEW)
    except ObjectDoesNotExist:
        raise ActionItemDeleteError(
            'Unable to delete action item. '
            f'Action item {action_cls.name} does not exist for '
            f'{subject_identifier}.')
    except MultipleObjectsReturned:
        action_cls.action_item_model_cls().objects.filter(
            subject_identifier=subject_identifier,
            action_type=action_cls.action_type(),
            status=NEW).delete()
    else:
        obj.delete()
    return None
