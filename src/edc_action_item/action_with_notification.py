from typing import List

from django.db import models

from .action import Action
from .action_item_notification import ActionItemNotification


class ActionWithNotification(Action):

    """A class mixin for the Action class that adds
    support for notifications.
    """

    notification_email_to: List[str] = None
    notification_display_name: str = None
    notification_fields: List[str] = None
    notification_super_cls = ActionItemNotification
    notify_on_changed_reference_obj: models.Model = True
    notify_on_close: bool = False
    notify_on_new: bool = False
    notify_on_new_and_no_reference_obj: bool = True
    notify_on_open: bool = False

    @classmethod
    def notification_cls(cls):
        """Returns a subclass of ActionItemModelNotification."""
        return type(
            f"{cls.__name__}Notification",
            (cls.notification_super_cls,),
            dict(
                name=f"{cls.name}-notification",
                notification_action_name=cls.name,
                display_name=(
                    cls.notification_display_name or f"{cls.display_name} Notification"
                ),
                email_to=cls.notification_email_to,
                notification_fields=cls.notification_fields,
                model=cls.get_reference_model(),
                notify_on_new_and_no_reference_obj=cls.notify_on_new_and_no_reference_obj,
                notify_on_new=cls.notify_on_new,
                notify_on_open=cls.notify_on_open,
                notify_on_close=cls.notify_on_close,
                notify_on_changed_reference_obj=cls.notify_on_changed_reference_obj,
            ),
        )
