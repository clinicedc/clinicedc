from django.core.exceptions import ObjectDoesNotExist
from edc_constants.constants import NEW, OPEN, CLOSED
from edc_notification import Notification
from edc_utils import get_utcnow

NOTIFY_ON_NEW_AND_NO_REFERENCE_OBJ = "notify_on_new_and_no_reference_obj"
NOTIFY_ON_NEW = "notify_on_new"
NOTIFY_ON_OPEN = "notify_on_open"
NOTIFY_ON_CLOSE = "notify_on_closed"
NOTIFY_ON_CHANGED_REFERENCE_OBJ = "notify_on_changed_reference_obj"


class ActionItemNotificationError(Exception):
    pass


class ActionItemNotification(Notification):

    """ A Notification class for the action item model.

    This class is the default superclass for an Action's
    notification class.

    See `Action.notification_cls()`

    * Sends an initial notification when an action or action_item
      is created (but only if the action item is created before
      the reference object is created);

    * Send an update notification if the reference object is changed.
      The reference object is considered changed if one of the values
      for a field listed in `notification_fields` is changed.

    """

    # set by default
    notification_action_name = None
    # set by class user, list of field(s) from
    # the action_item.reference_obj
    notification_fields = []

    # action_item created before the reference obj
    notify_on_new_and_no_reference_obj = True
    # reference obj creates action_item and status set to OPEN
    notify_on_open = False
    # action_item status set to CLOSED
    notify_on_closed = False
    # reference obj changed, action item status set to OPEN
    notify_on_changed_reference_obj = True
    # set by default to the the Action's reference_model
    model = None

    email_subject_template = (
        "{updated_subject_line}{test_subject_line}{protocol_name}: "
        "{display_name} "
        "for {subject_identifier}"
    )
    email_body_template_new = (
        "\n\nDo not reply to this email\n\n"
        "{test_body_line}"
        'A report titled "{parent_reference_verbose_name}" has been submitted '
        "for patient {subject_identifier} "
        "at the {site_name} site which requires additional information.\n\n"
        "Please complete the following report:\n\n"
        "Title: {display_name}.\n\n"
        "You received this message because you are subscribed to receive these "
        "notifications in your user profile.\n\n"
        "{test_body_line}"
        "Thanks."
    )
    email_body_template_update = (
        "\n\nDo not reply to this email\n\n"
        "{test_body_line}"
        "An updated report has been submitted.\n\n"
        'The information related to the report "{display_name}" for patient '
        "{subject_identifier} "
        "at the {site_name} site has changed. You may wish to review.\n\n"
        "You received this message because you are subscribed to receive these "
        "notifications in your user profile.\n\n"
        "{test_body_line}"
        "Thanks."
    )
    email_footer_template = (
        "\n\n-----------------\n"
        'To unsubscribe remove "{display_name}" from your chosen '
        "email notifications in your user profile.\n\n"
        "{name}\n"
        "{notification_reason}:{pk}\n"
        "{message_datetime} (UTC)"
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.updated_subject_line = ""
        self.updated_body_line = ""

    def notify_on(self, action_item=None, reference_obj=None):
        updated = False
        if (
            self.notify_on_new_and_no_reference_obj
            and action_item.status == NEW
            and not reference_obj
        ):
            notify = NOTIFY_ON_NEW_AND_NO_REFERENCE_OBJ
        elif self.notify_on_new and action_item.status == NEW and reference_obj:
            notify = NOTIFY_ON_NEW
        elif self.notify_on_open and action_item.status == OPEN and reference_obj:
            notify = NOTIFY_ON_OPEN
        elif self.notify_on_closed and action_item.status == CLOSED and reference_obj:
            notify = NOTIFY_ON_CLOSE
        elif (
            self.notify_on_changed_reference_obj
            and action_item.status != NEW
            and reference_obj
        ):
            notify = NOTIFY_ON_CHANGED_REFERENCE_OBJ
            updated = True
        else:
            notify = False
        return notify, updated

    def notify(self, force_notify=None, use_email=None, use_sms=None, **kwargs):
        """Overridden to only call `notify` if action name matches.
        """
        notified = False
        instance = kwargs.get("instance")
        if instance._meta.label_lower == "edc_action_item.actionitem":
            try:
                action_name = instance.action_type.name
            except AttributeError:
                pass
            else:
                if action_name == self.notification_action_name:
                    action_item = kwargs.get("instance")
                    reference_obj = self.get_reference_obj(action_item)

                    notify, updated = self.notify_on(
                        action_item=action_item, reference_obj=reference_obj
                    )

                    kwargs.update(updated=updated)
                    kwargs.update(instance=reference_obj)
                    kwargs.update(action_item=action_item)

                    if notify:
                        try:
                            parent_reference_verbose_name = (
                                action_item.parent_action_item.reference_obj._meta.verbose_name
                            )
                        except AttributeError:
                            parent_reference_verbose_name = (
                                action_item.reference_model_cls()._meta.verbose_name
                            )
                        email_body_template = (
                            self.email_body_template_update
                            if updated
                            else self.email_body_template_new
                        )
                        kwargs.update(
                            notification_reason=notify,
                            updated=updated,
                            parent_reference_verbose_name=parent_reference_verbose_name,
                            subject_identifier=action_item.subject_identifier,
                            site_name=action_item.site.name,
                            pk=action_item.pk,
                        )
                        notified = super().notify(
                            force_notify=force_notify,
                            use_email=use_email,
                            use_sms=use_sms,
                            email_body_template=email_body_template,
                            **kwargs
                        )
        return notified

    def notify_on_condition(self, **kwargs):
        notify_on_condition = False
        updated = kwargs.get("updated")
        reference_obj = kwargs.get("instance")
        action_item = kwargs.get("action_item")
        if not reference_obj:
            emailed = action_item.emailed
        else:
            emailed = reference_obj.action_item.emailed
        if not emailed and not updated:
            self.updated_subject_line = ""
            self.updated_body_line = "A report"
            notify_on_condition = True
        elif updated:
            self.updated_subject_line = "*UPDATE* "
            self.updated_body_line = "An updated report"
            notify_on_condition = True
        return notify_on_condition

    def get_reference_obj(self, action_item):
        try:
            reference_obj = action_item.reference_obj
        except ObjectDoesNotExist:
            reference_obj = None
        return reference_obj

    def get_action_name(self, instance):
        """Returns that action_name.
        """
        try:
            action_name = instance.action_item.action_cls.name
        except AttributeError:
            try:
                action_name = instance.action_type.name
            except AttributeError:
                action_name = None
        return action_name

    def get_template_options(self, **kwargs):
        template_options = super().get_template_options(**kwargs)
        template_options.update(
            updated_subject_line=self.updated_subject_line,
            updated_body_line=self.updated_body_line,
        )
        return template_options

    def post_notification_actions(self, email_sent=None, **kwargs):
        """Record the datetime of first email sent.
        """
        action_item = kwargs.get("action_item")
        if email_sent and not action_item.emailed:
            action_item.emailed = True
            action_item.emailed_datetime = get_utcnow()
            action_item.save_without_historical_record()
