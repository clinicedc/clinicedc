from django.apps import apps as django_apps
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from ..mail import EmailMessage, MailingListManager
from ..site_notifications import site_notifications


class Notification:

    app_name = None
    name = None
    display_name = None
    email_from = settings.EMAIL_CONTACTS.get('data_manager')
    email_to = None
    email_message_cls = EmailMessage
    mailing_list_manager_cls = MailingListManager
    body_template = (
        '\n\nDo not reply to this email\n\n'
        '{body_test_line}'
        'A report has been submitted for patient '
        '{instance.subject_identifier} '
        'at site {instance.site.name} which may require '
        'your attention.\n\n'
        'Title: {display_name}\n\n'
        'You received this message because you are subscribed to receive these '
        'notifications in your user profile.\n\n'
        '{body_test_line}'
        'Thanks.')
    subject_template = (
        '{subject_test_line}{updated}{protocol_name}: '
        '{display_name} '
        'for {instance.subject_identifier}')
    body_test_line = 'THIS IS A TEST MESSAGE. NO ACTION IS REQUIRED\n\n'
    subject_test_line = 'TEST/UAT -- '

    def __init__(self):
        self.email_to = self.email_to or [
            f'{self.name}.{settings.APP_NAME}@mg.clinicedc.org']
        self.protocol_name = django_apps.get_app_config(
            'edc_protocol').protocol_name
        self.mailing_list_manager = self.mailing_list_manager_cls(
            email_to=self.email_to,
            display_name=self.display_name,
            name=self.name)

    def __str__(self):
        return f'{self.name}: {self.display_name}'

    def callback(self, instance=None, created=None, test=None, **kwargs):
        return False

    def notify(self, **kwargs):
        NotificationModel = django_apps.get_model(
            'edc_notification.notification')
        try:
            obj = NotificationModel.objects.get(name=self.name)
        except ObjectDoesNotExist:
            site_notifications.update_notification_list()
            obj = NotificationModel.objects.get(name=self.name)
        if obj.enabled and self.callback(**kwargs):
            email_message = self.email_message_cls(
                notification=self, **kwargs)
            email_message.send()
