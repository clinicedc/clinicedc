from django.apps import apps as django_apps
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from twilio.base.exceptions import TwilioRestException, TwilioException
from twilio.rest import Client


class UnknownUser(Exception):
    pass


class SmsNotEnabled(Exception):
    pass


class SmsMessage:

    #     def __init__(self, notification=None, instance=None, user=None, **kwargs):
    #         self.template_opts = {}
    #         try:
    #             self.live_system = settings.LIVE_SYSTEM
    #         except AttributeError:
    #             self.live_system = False
    #         try:
    #             self.user = django_apps.get_model(
    #                 'auth.user').objects.get(username=user)
    #         except ObjectDoesNotExist as e:
    #             raise UnknownUser(f'{e}. Got username={user}.')
    #         self.notification = notification
    #         try:
    #             self.enabled = settings.TWILIO_ENABLED
    #         except AttributeError:
    #             self.enabled = False
    #         try:
    #             self.sms_to = self.user.userprofile.mobile
    #         except AttributeError:
    #             self.sms_to = False
    #         protocol_name = django_apps.get_app_config(
    #             'edc_protocol').protocol_name
    #         self.body = self.get_sms_template().format(
    #             sms_test_line=self.get_sms_test_line(),
    #             display_name=self.notification.display_name,
    #             protocol_name=protocol_name,
    #             instance=instance)

    def send(self, fail_silently=None, sender=None, recipient=None):
        if self.enabled and self.sms_to:
            try:
                client = Client()
            except (TwilioRestException, TwilioException):
                if not fail_silently:
                    raise
            else:
                sender = sender or getattr(settings, 'TWILIO_SENDER', None)
                recipient = recipient or self.user.userprofile.mobile
                try:
                    message = client.messages.create(
                        from_=sender,
                        to=recipient,
                        body=self.body)
                except (TwilioRestException, TwilioException):
                    if not fail_silently:
                        raise
                else:
                    return message.sid
        return None

    def get_sms_template(self):
        return self.notification.sms_template or self.sms_template

    def get_sms_test_line(self):
        if not self.live_system:
            return self.notification.sms_test_line or self.sms_test_line
        return ''
