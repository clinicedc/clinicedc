import os
import sys

from django.apps import apps as django_apps
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client


class UnknownUser(Exception):
    pass


class SmsNotEnabled(Exception):
    pass


class SmsMessage:

    sms_template = (
        '{sms_test_line}{protocol_name}: Report "{display_name}" for '
        'patient {instance.subject_identifier} '
        'at site {instance.site.name} may require '
        'your attention. Login to review.')
    sms_test_line = 'TEST MESSAGE. NO ACTION REQUIRED - '

    def __init__(self, notification=None, instance=None, user=None, **kwargs):
        self.user = user
        self.template_opts = {}
        try:
            self.live_system = settings.LIVE_SYSTEM
        except AttributeError:
            self.live_system = False
        try:
            user = django_apps.get_model(
                'auth.user').objects.get(username=user)
        except ObjectDoesNotExist as e:
            raise UnknownUser(f'{e}. Got username={user}.')
        self.protocol_name = django_apps.get_app_config(
            'edc_protocol').protocol_name
        self.instance = instance
        self.notification = notification
        self.sms_to = user.userprofile.mobile
        self.body = self.get_sms_template().format(
            sms_test_line=self.get_sms_test_line(),
            display_name=self.notification.display_name,
            protocol_name=self.protocol_name,
            instance=self.instance)
        try:
            self.enabled = settings.TWILIO_ENABLED
        except AttributeError:
            self.enabled = False
        else:
            self.sms_from = settings.TWILIO_SENDER

    def send(self):
        if not self.enabled:
            raise SmsNotEnabled(
                f'SMS is not enabled. Failed to send notifiction '
                f'\'{self.notification.display_name}\' for \'{self.user}\'. '
                f'See settings.TWILIO_ENABLED')
        if self.sms_to:
            # get credentials from ENV
            client = Client()
            try:
                message = client.messages.create(
                    from_=os.environ['TWILIO_SENDER'],
                    to=self.sms_to,
                    body=self.body)
            except TwilioRestException as e:
                sys.stdout.write(f'{e}')
            else:
                return message.sid
        return None

    def get_sms_template(self):
        return self.notification.sms_template or self.sms_template

    def get_sms_test_line(self):
        if not self.live_system:
            return self.notification.sms_test_line or self.sms_test_line
        return ''
