from edc_base import get_utcnow
from edc_notification import ModelNotification


class ActionItemNotificationError(Exception):
    pass


class ActionItemModelNotification(ModelNotification):

    """Subclass of ModelNotification that handles both NEW
    and UPDATED model instances.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.updated_subject_line = ''
        self.updated_body_line = ''

    notification_fields = []
    email_subject_template = (
        '{updated_subject_line}{test_subject_line}{protocol_name}: '
        '{display_name} '
        'for {instance.subject_identifier}')
    email_body_template = (
        '\n\nDo not reply to this email\n\n'
        '{test_body_line}'
        '{updated_body_line} has been submitted for patient '
        '{instance.subject_identifier} '
        'at site {instance.site.name} which may require '
        'your attention.\n\n'
        'Title: {display_name}\n\n'
        'You received this message because you are subscribed to receive these '
        'notifications in your user profile.\n\n'
        '{test_body_line}'
        'Thanks.')

    def notify_on_condition(self, **kwargs):
        instance = kwargs.get('instance')
        if self.name == instance.action_name:
            if instance.history.all().count() == 1:
                self.updated_subject_line = ''
                self.updated_body_line = 'A report'
                return True
            elif self.notification_fields and instance.history.all().count() > 1:
                updated = self.notification_model_is_changed(instance)
                if updated:
                    self.updated_subject_line = '*UPDATE* '
                    self.updated_body_line = 'An updated report'
                return updated
        return False

    @property
    def extra_template_options(self):
        return dict(
            updated_subject_line=self.updated_subject_line,
            updated_body_line=self.updated_body_line)

    def notification_model_is_changed(self, instance):
        changed_fields = {}
        if instance._meta.label_lower == self.model:
            changes = {}
            for field in self.notification_fields:
                field_values = [
                    getattr(obj, field)
                    for obj in instance.history.all().order_by(
                        'history_date')]
                field_values.reverse()
                changes.update({field: field_values[:2]})
            for field, values in changes.items():
                try:
                    changed = values[0] != values[1]
                except IndexError:
                    pass
                else:
                    if changed:
                        changed_fields.update({field: values})
        return changed_fields

    def post_notification_actions(self, email_sent=None, **kwargs):
        """Record the datetime of first email sent.
        """
        instance = kwargs.get('instance')
        if email_sent and not instance.action_item.emailed:
            instance.action_item.emailed = True
            instance.action_item.emailed_datetime = get_utcnow()
            instance.action_item.save_without_historical_record()


class ActionNotificationMixin:

    """A mixin for the Action class to add support for notifications.
    """

    notifications_enabled = True
    notification_super_cls = ActionItemModelNotification
    notification_name = None
    notification_display_name = None
    notification_fields = None

    @classmethod
    def notification_cls(cls):
        """Returns a subclass of ActionItemModelNotification or None.

        Important: notification_cls.name must match the cls.name.
        """
        if cls.notifications_enabled:
            return type(
                cls.name.title(),
                (cls.notification_super_cls, ),
                dict(name=cls.name,
                     display_name=(
                         cls.notification_display_name or cls.display_name),
                     model=cls.reference_model,
                     notification_fields=cls.notification_fields))
        return None
