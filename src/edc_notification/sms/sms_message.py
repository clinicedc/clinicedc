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

    sms_template = (
        '{sms_test_line}{protocol_name}: Report "{display_name}" for '
        'patient {instance.subject_identifier} '
        'at site {instance.site.name} may require '
        'your attention. Login to review.')
    sms_test_line = 'TEST MESSAGE. NO ACTION REQUIRED - '

    def __init__(self, notification=None, instance=None, user=None, **kwargs):
        self.template_opts = {}
        try:
            self.live_system = settings.LIVE_SYSTEM
        except AttributeError:
            self.live_system = False
        try:
            self.user = django_apps.get_model(
                'auth.user').objects.get(username=user)
        except ObjectDoesNotExist as e:
            raise UnknownUser(f'{e}. Got username={user}.')
        self.notification = notification
        try:
            self.enabled = settings.TWILIO_ENABLED
        except AttributeError:
            self.enabled = False
        try:
            self.sms_to = self.user.userprofile.mobile
        except AttributeError:
            self.sms_to = False
        protocol_name = django_apps.get_app_config(
            'edc_protocol').protocol_name
        self.body = self.get_sms_template().format(
            sms_test_line=self.get_sms_test_line(),
            display_name=self.notification.display_name,
            protocol_name=protocol_name,
            instance=instance)

    def send(self, fail_silently=None):
        if self.enabled and self.sms_to:
            try:
                client = Client()
            except (TwilioRestException, TwilioException):
                if not fail_silently:
                    raise
            else:
                try:
                    message = client.messages.create(
                        from_=settings.TWILIO_SENDER,
                        to=self.user.userprofile.mobile,
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
