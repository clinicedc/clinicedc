from .site_action_items import site_action_items
from .action import Action


class RegisterNotificationError(Exception):
    pass


def register(**kwargs):
    """Registers a action_cls.
    """

    def _wrapper(action_cls):

        if not issubclass(action_cls, (Action,)):
            raise RegisterNotificationError(
                f"Wrapped class must a Action class. Got {action_cls}"
            )

        site_action_items.register(action_cls=action_cls)

        return action_cls

    return _wrapper
