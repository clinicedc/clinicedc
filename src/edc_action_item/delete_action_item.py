from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from edc_constants.constants import NEW

from .get_action_type import get_action_type


class ActionItemDeleteError(Exception):
    pass


def delete_action_item(action_cls=None, subject_identifier=None, using=None):
    """Deletes any NEW action items for a given class
    and subject_identifier.
    """
    try:
        obj = (
            action_cls.action_item_model_cls()
            .objects.using(using)
            .get(
                subject_identifier=subject_identifier,
                action_type=get_action_type(action_cls),
                status=NEW,
            )
        )
    except ObjectDoesNotExist:
        raise ActionItemDeleteError(
            "Unable to delete action item. "
            f"Action item {action_cls.name} does not exist for "
            f"{subject_identifier}."
        )
    except MultipleObjectsReturned:
        for obj in (
            action_cls.action_item_model_cls()
            .objects.using(using)
            .filter(
                subject_identifier=subject_identifier,
                action_type=get_action_type(action_cls),
                status=NEW,
            )
        ):
            obj.delete(using=using)
    else:
        obj.delete(using=using)
    return None
