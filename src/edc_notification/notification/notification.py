from copy import copy
from django.apps import apps as django_apps
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMessage
from twilio.base.exceptions import TwilioRestException, TwilioException
from twilio.rest import Client

from ..mailing_list_creator import MailingListCreator
from ..site_notifications import site_notifications
from ..sms_message import SmsMessage


class NotificationError(Exception):
    pass


class Notification:

    app_name = None
    name = 'undefined'
    display_name = None

    email_from = settings.EMAIL_CONTACTS.get('data_manager')
    email_to = None
    email_message_cls = EmailMessage
    mailing_list_manager_cls = MailingListCreator

    email_body_template = (
        '\n\nDo not reply to this email\n\n'
        '{test_body_line}'
        'A report has been submitted for patient '
        '{subject_identifier} '
        'at site {site_name} which may require '
        'your attention.\n\n'
        'Title: {display_name}\n\n'
        'You received this message because you are subscribed to receive these '
        'notifications in your user profile.\n\n'
        '{test_body_line}'
        'Thanks.')
    email_subject_template = (
        '{test_subject_line}{protocol_name}: '
        '{display_name} '
        'for {subject_identifier}')
    email_test_body_line = 'THIS IS A TEST MESSAGE. NO ACTION IS REQUIRED\n\n'
    email_test_subject_line = 'TEST/UAT -- '

    sms_message_cls = SmsMessage
    sms_template = (
        '{test_line}{protocol_name}: Report "{display_name}" for '
        'patient {subject_identifier} '
        'at site {site_name} may require '
        'your attention. Login to review.')
    sms_test_line = 'TEST MESSAGE. NO ACTION REQUIRED - '

    def __init__(self):
        self._notification_enabled = None
        self._template_opts = {}
        self.email_to = self.email_to or [
            f'{self.name}.{settings.APP_NAME}@mg.clinicedc.org']
        try:
            live_system = settings.LIVE_SYSTEM
        except AttributeError:
            live_system = False
        if not live_system:
            self.email_to = [f'test.{email}' for email in self.email_to]
        self.mailing_list_manager = self.mailing_list_manager_cls(
            email_to=self.email_to,
            display_name=self.display_name,
            name=self.name)

    def __str__(self):
        return f'{self.name}: {self.display_name}'

    def notify(self, force_notify=None, use_email=None, use_sms=None, **kwargs):
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
        use_email = use_email or getattr(settings, 'EMAIL_ENABLED', False)
        use_sms = use_sms or getattr(settings, 'TWILIO_ENABLED', False)
        if force_notify or self._notify_on_condition(**kwargs):
            if use_email:
                email_sent = self.send_email(**kwargs)
            if use_sms:
                sms_sent = self.send_sms(**kwargs)
        self.post_notification_actions(
            email_sent=email_sent, sms_sent=sms_sent)

    def notify_on_condition(self, **kwargs):
        """Override to return True if the notification
        should be sent by email and/or sms.

        A return value of `False` means nothing will be sent.
        """
        return False

    def _notify_on_condition(self, test_message=None, **kwargs):
        """Returns the value of `notify_on_condition` or False.
        """
        if self.enabled or test_message:
            return test_message or self.notify_on_condition(**kwargs)
        return False

    def post_notification_actions(self, email_sent=None, sms_sent=None):
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
            # trigger exception if this class is not registered.
            site_notifications.get(self.name)

            NotificationModel = django_apps.get_model(
                'edc_notification.notification')
            try:
                obj = NotificationModel.objects.get(name=self.name)
            except ObjectDoesNotExist:
                site_notifications.update_notification_list()
                obj = NotificationModel.objects.get(name=self.name)
            self._notification_enabled = obj.enabled
        return self._notification_enabled

    @property
    def template_options(self):
        """Returns a dictionary of message template options.

        Extend using `extra_template_options`.
        """
        protocol_name = django_apps.get_app_config(
            'edc_protocol').protocol_name
        template_options = dict(
            name=self.name,
            protocol_name=protocol_name,
            display_name=self.display_name,
            email_from=self.email_from)
        template_options.update(**self.extra_template_options)
        return template_options

    @property
    def extra_template_options(self):
        """Override to return a dictionary of extra message
        template options.

        See also: `template_options`
        """
        return {}

    def send_email(self, fail_silently=None, email_to=None, **kwargs):
        opts = copy(self.template_options)
        opts.update(
            test_subject_line=(
                self.email_test_subject_line if kwargs.get('test_message') else '').strip(),
            test_body_line=self.email_test_body_line if kwargs.get('test_message') else '')
        opts.update(**kwargs)
        subject = self.email_subject_template.format(**opts)
        body = self.email_body_template.format(**opts)
        args = [
            subject, body,
            self.email_from,
            email_to or self.email_to]
        email = self.email_message_cls(*args)
        return email.send(fail_silently)

    def send_sms(self, fail_silently=None, sms_recipient=None, **kwargs):
        status = {}
        if self.sms_sender:
            opts = copy(self.template_options)
            opts.update(
                test_line=self.sms_test_line if kwargs.get(
                    'test_message') else '',
                **kwargs)
            body = self.sms_template.format(**opts)
            try:
                client = Client()
            except (TwilioRestException, TwilioException):
                if not fail_silently:
                    raise
            else:
                recipients = (
                    [sms_recipient] if sms_recipient else self.sms_recipients)
                for recipient in recipients:
                    try:
                        message = client.messages.create(
                            from_=self.sms_sender,
                            to=recipient,
                            body=body)
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
        UserProfile = django_apps.get_model('edc_auth.UserProfile')
        for user_profile in UserProfile.objects.filter(
                user__is_active=True, user__is_staff=True):
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
        return dict(subject_identifier='123456910', site_name='Gaborone')

    def send_test_email(self, email_to):
        """Sends a test message to "email_to".

        For example:

            from edc_notification.notification import Notification

            notification = Notification()
            notification.send_test_email('someone@example.com')
        """
        self.notify(force_notify=True, test_message=True,
                    email_to=[email_to],
                    **self.test_template_options)

    def send_test_sms(self, sms_recipient=None):
        """Sends a test message to "email_to".

        For example:

            from edc_notification.notification import Notification

            notification = Notification()
            notification.send_test_sms(sms_recipient='+123456789')
        """
        self.notify(force_notify=True, test_message=True,
                    sms_recipient=sms_recipient,
                    ** self.test_template_options)
