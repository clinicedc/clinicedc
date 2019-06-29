from django.core.exceptions import ObjectDoesNotExist

from .create_or_update_action_type import create_or_update_action_type


def get_action_type(cls, name=None, using=None):
    """Returns the ActionType model instance.
    """
    try:
        action_type = (
            cls.action_type_model_cls().objects.using(using).get(name=name or cls.name)
        )
    except ObjectDoesNotExist:
        action_type = create_or_update_action_type(using=using, **cls.as_dict())
    return action_type
