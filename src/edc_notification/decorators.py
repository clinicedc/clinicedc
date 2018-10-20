from .notification import Notification
from .site_notifications import site_notifications


class RegisterNotificationError(Exception):
    pass


def register(**kwargs):
    """Registers a notification_cls.
    """
    def _wrapper(notification_cls):

        if not issubclass(notification_cls, (Notification, )):
            raise RegisterNotificationError(
                f'Wrapped class must a Notification class. Got {notification_cls}')

        site_notifications.register(notification_cls=notification_cls)

        return notification_cls
    return _wrapper
