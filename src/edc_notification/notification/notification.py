from django.apps import apps as django_apps
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMessage
from edc_protocol import Protocol
from edc_utils import get_utcnow
from twilio.base.exceptions import TwilioRestException, TwilioException
from twilio.rest import Client

from ..site_notifications import site_notifications


class NotificationError(Exception):
    pass


class Notification:
    app_name = None
    name = None
    display_name = None

    sms_client = Client

    email_from = settings.EMAIL_CONTACTS.get("data_manager")
    email_to = None  # usually a mailing list address
    email_message_cls = EmailMessage

    email_body_template = (
        "\n\nDo not reply to this email\n\n"
        "{test_body_line}"
        "A report has been submitted for patient "
        "{subject_identifier} "
        "at site {site_name} which may require "
        "your attention.\n\n"
        "Title: {display_name}\n\n"
        "You received this message because you are subscribed to receive these "
        "notifications in your user profile.\n\n"
        "{test_body_line}"
        "Thanks."
    )
    email_subject_template = (
        "{test_subject_line}{protocol_name}: "
        "{display_name} "
        "for {subject_identifier}"
    )
    email_footer_template = (
        "\n\n-----------------\n"
        'To unsubscribe remove "{display_name}" from your chosen '
        "email notifications in your user profile.\n\n"
        "{name}\n"
        "{message_reference}\n"
        "{message_datetime} (UTC)"
    )
    email_test_body_line = "THIS IS A TEST MESSAGE. NO ACTION IS REQUIRED\n\n"
    email_test_subject_line = "TEST/UAT -- "

    sms_template = (
        '{test_line}{protocol_name}: Report "{display_name}" for '
        "patient {subject_identifier} "
        "at site {site_name} may require "
        "your attention. Login to review."
    )
    sms_test_line = "TEST MESSAGE. NO ACTION REQUIRED - "

    def __init__(self):
        self._notification_enabled = None
        self._template_opts = {}
        self.email_to = self.email_to or self.default_email_to
        self.test_message = False
        try:
            live_system = settings.LIVE_SYSTEM
        except AttributeError:
            live_system = False
        if not live_system:
            self.email_to = [f"test.{email}" for email in self.email_to]
            self.test_message = True

    def __repr__(self):
        return (
            f"<{self.__class__.__name__}:name='{self.name}', "
            f"display_name='{self.display_name}'>"
        )

    def __str__(self):
        return f"{self.name}: {self.display_name}"

    @property
    def default_email_to(self):
        return [f"{self.name}.{settings.APP_NAME}@mg.clinicedc.org"]

    def notify(
        self,
        force_notify=None,
        use_email=None,
        use_sms=None,
        email_body_template=None,
        **kwargs,
    ):
        """Notify / send an email and/or SMS.

        Main entry point.

        This notification class (me) knows from whom and to whom the
        notifications will be sent.

        See signals and kwargs are:
            * history_instance
            * instance
            * user
        """
        email_sent = None
        sms_sent = None
        use_email = use_email or getattr(settings, "EMAIL_ENABLED", False)
        use_sms = use_sms or getattr(settings, "TWILIO_ENABLED", False)
        if force_notify or self._notify_on_condition(**kwargs):
            if use_email:
                email_body_template = (
                    email_body_template or self.email_body_template
                ) + self.email_footer_template
                email_sent = self.send_email(
                    email_body_template=email_body_template, **kwargs
                )
            if use_sms:
                sms_sent = self.send_sms(**kwargs)
            self.post_notification_actions(
                email_sent=email_sent, sms_sent=sms_sent, **kwargs
            )
        return True if email_sent or sms_sent else False

    def notify_on_condition(self, **kwargs):
        """Override to conditionally return True if the notification
        should be sent by email and/or sms.

        A return value of `False` means nothing will be sent.
        """
        return True

    def _notify_on_condition(self, test_message=None, **kwargs):
        """Returns the value of `notify_on_condition` or False.
        """
        if test_message:
            return True
        else:
            return self.enabled and self.notify_on_condition(**kwargs)

    def post_notification_actions(self, **kwargs):
        pass

    @property
    def enabled(self):
        """Returns True if this notification is enabled based on the value
        of Notification model instance.

        Note: Notification names/display_names are persisted in the
        "Notification" model where each mode instance can be flagged
        as enabled or not, and are selected/subscribed to by
        each user in their user profile.

        See also: `site_notifications.update_notification_list`
        """
        if not self._notification_enabled:
            self._notification_enabled = self.notification_model.enabled
        return self._notification_enabled

    @property
    def notification_model(self):
        """Returns the Notification 'model' instance associated
        with this notification.
        """
        NotificationModel = django_apps.get_model("edc_notification.notification")
        # trigger exception if this class is not registered.
        site_notifications.get(self.name)
        try:
            notification_model = NotificationModel.objects.get(name=self.name)
        except ObjectDoesNotExist:
            site_notifications.update_notification_list()
            notification_model = NotificationModel.objects.get(name=self.name)
        return notification_model

    def get_template_options(self, instance=None, test_message=None, **kwargs):
        """Returns a dictionary of message template options.

        Extend using `extra_template_options`.
        """
        test_message = test_message or self.test_message
        template_options = dict(
            name=self.name,
            protocol_name=Protocol().protocol_name,
            display_name=self.display_name,
            email_from=self.email_from,
            test_subject_line=(
                self.email_test_subject_line if test_message else ""
            ).strip(),
            test_body_line=self.email_test_body_line if test_message else "",
            test_line=self.sms_test_line if test_message else "",
            message_datetime=get_utcnow(),
            message_reference="",
        )
        if "subject_identifier" not in template_options:
            try:
                template_options.update(subject_identifier=instance.subject_identifier)
            except AttributeError:
                pass
        if "site_name" not in template_options:
            try:
                template_options.update(site_name=instance.site.name.title())
            except AttributeError:
                pass
        return template_options

    def send_email(
        self, fail_silently=None, email_to=None, email_body_template=None, **kwargs
    ):
        kwargs.update(**self.get_template_options(**kwargs))
        subject = self.email_subject_template.format(**kwargs)
        body = (email_body_template or self.email_body_template).format(**kwargs)
        email = self.email_message_cls(
            subject, body, self.email_from, email_to or self.email_to
        )
        return email.send(fail_silently)

    def send_sms(self, fail_silently=None, sms_recipient=None, **kwargs):
        status = {}
        if self.sms_sender:
            kwargs.update(**self.get_template_options(**kwargs))
            body = self.sms_template.format(**kwargs)
            try:
                client = self.sms_client()
            except (TwilioRestException, TwilioException):
                if not fail_silently:
                    raise
            else:
                recipients = [sms_recipient] if sms_recipient else self.sms_recipients
                for recipient in recipients:
                    try:
                        message = client.messages.create(
                            from_=self.sms_sender, to=recipient, body=body
                        )
                    except (TwilioRestException, TwilioException):
                        if not fail_silently:
                            raise
                    else:
                        status.update({recipient: message.sid})
        return status

    @property
    def sms_sender(self):
        try:
            sender = settings.TWILIO_SENDER
        except AttributeError:
            sender = None
        return sender

    @property
    def sms_recipients(self):
        """Returns a list of recipients subscribed to receive SMS's
        for this "notifications" class.

        See also: edc_auth.UserProfile.
        """
        sms_recipients = []
        UserProfile = django_apps.get_model("edc_auth.UserProfile")
        for user_profile in UserProfile.objects.filter(
            user__is_active=True, user__is_staff=True
        ):
            try:
                user_profile.sms_notifications.get(name=self.name)
            except ObjectDoesNotExist:
                pass
            else:
                if user_profile.mobile:
                    sms_recipients.append(user_profile.mobile)
        return sms_recipients

    @property
    def test_template_options(self):
        return dict(subject_identifier="123456910", site_name="Gaborone")

    def send_test_email(self, email_to):
        """Sends a test message to "email_to".

        For example:

            from edc_notification.notification import Notification

            notification = Notification()
            notification.send_test_email('someone@example.com')
        """
        self.notify(
            force_notify=True,
            test_message=True,
            email_to=[email_to],
            **self.test_template_options,
        )

    def send_test_sms(self, sms_recipient=None):
        """Sends a test message to "email_to".

        For example:

            from edc_notification.notification import Notification

            notification = Notification()
            notification.send_test_sms(sms_recipient='+123456789')
        """
        self.notify(
            force_notify=True,
            test_message=True,
            sms_recipient=sms_recipient,
            **self.test_template_options,
        )
