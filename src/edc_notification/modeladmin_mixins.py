from django.utils.safestring import mark_safe

from .site_notifications import site_notifications


class NotificationModelAdminMixin:

    """Show some information about which notifications are
    linked to the form and of those which are the current
    user subscribed to.

    Requires to be declared together with `ModelAdminFormInstructionsMixin`
    from module `edc_model_admin`.
    """

    def get_notification_instructions(self, request=None):
        notifications = site_notifications.models.get(self.model._meta.label_lower)
        notification_instructions = None
        if notifications:
            notifications = [
                notification.display_name for notification in notifications
            ]
            tooltip1 = mark_safe(", ".join(notifications))
            my_notifications = [
                n.display_name
                for n in request.user.userprofile.email_notifications.filter(
                    display_name__in=notifications
                )
            ]
            tooltip2 = mark_safe(", ".join(my_notifications))
            word = "notification is" if len(notifications) == 1 else "notifications are"
            notification_instructions = (
                f'<a href="#" title="{tooltip1}">{len(notifications)} '
                f"{word}</a> enabled for this form. "
                f'You are <a href="#" title="{tooltip2}">subscribed '
                f"to {len(my_notifications)}</a>. "
                f"See your user profile for more details."
            )
            return mark_safe(notification_instructions)
        return notification_instructions

    def get_add_instructions(self, extra_context, request=None):
        extra_context = super().get_add_instructions(extra_context)
        extra_context["notification_instructions"] = self.get_notification_instructions(
            request
        )
        return extra_context

    def get_change_instructions(self, extra_context, request=None):
        extra_context = super().get_add_instructions(extra_context)
        extra_context["notification_instructions"] = self.get_notification_instructions(
            request
        )
        return extra_context
