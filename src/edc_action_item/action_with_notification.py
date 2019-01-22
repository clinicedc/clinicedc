from .action import Action
from .action_item_notification import ActionItemNotification


class ActionWithNotification(Action):

    """A class mixin for the Action class that adds
    support for notifications.
    """

    notification_email_to = None
    notification_display_name = None
    notification_fields = None
    notification_super_cls = ActionItemNotification
    notify_on_changed_reference_obj = True
    notify_on_close = False
    notify_on_new = False
    notify_on_new_and_no_reference_obj = True
    notify_on_open = False

    @classmethod
    def notification_cls(action_cls):
        """Returns a subclass of ActionItemModelNotification.
        """
        return type(
            f"{action_cls.__name__}Notification",
            (action_cls.notification_super_cls,),
            dict(
                name=f"{action_cls.name}-notification",
                notification_action_name=action_cls.name,
                display_name=(
                    action_cls.notification_display_name
                    or f"{action_cls.display_name} Notification"
                ),
                email_to=action_cls.notification_email_to,
                notification_fields=action_cls.notification_fields,
                model=action_cls.reference_model,
                notify_on_new_and_no_reference_obj=(
                    action_cls.notify_on_new_and_no_reference_obj
                ),
                notify_on_new=action_cls.notify_on_new,
                notify_on_open=action_cls.notify_on_open,
                notify_on_close=action_cls.notify_on_close,
                notify_on_changed_reference_obj=action_cls.notify_on_changed_reference_obj,
            ),
        )
