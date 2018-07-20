from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from edc_constants.constants import NEW


class SingletonActionItemError(Exception):
    pass


class ActionItemDeleteError(Exception):
    pass


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
