from django.apps import apps as django_apps
from django.core import mail

from .constants import EMAIL


class Notification:

    name = None
    display_name = None
    subject_template = (
        '{test_subject}{updated}{protocol_name}: '
        '{display_name} '
        'for {instance.subject_identifier}')
    message_template = (
        '\n\nDo not reply to this email\n\n'
        '{test_message}'
        'A report has been submitted for patient '
        '{instance.subject_identifier} '
        'at site {instance.site.name} which may require '
        'your attention.\n\n'
        'Title: {display_name}\n\n'
        'You received this message because you are subscribed to receive these '
        'notifications in your user profile.\n\n'
        '{test_message}'
        'Thanks.')
    email_from = 'data_manager@mg.clinicedc.org'
    email_to = ['user@example.com']
    message_modes = [EMAIL]
    test_message = 'THIS IS A TEST MESSAGE. NO ACTION IS REQUIRED\n\n'
    test_subject = 'TEST/UAT -- '

    def __init__(self, instance=None, created=None, test=None,
                 updated=None, **kwargs):
        edc_protocol_app_config = django_apps.get_app_config('edc_protocol')
        self.instance = instance
        self.created = created
        self.test = test
        self.updated = updated
        self.protocol_name = edc_protocol_app_config.protocol_name
        for k, v in kwargs.items():
            setattr(self, k, v)

    def callback(self):
        return False

    def notify(self):
        if self.callback():
            connection = mail.get_connection()
            email = mail.EmailMessage(
                self.subject,
                self.body,
                self.email_from,
                self.email_to,
                connection=connection)
            email.send()

    @property
    def subject(self):
        return self.subject_template.format(
            test_subject=self.test_subject if self.test else '',
            name=self.name,
            display_name=self.display_name,
            **self.__dict__)

    @property
    def body(self):
        return self.message_template.format(
            test_message=self.test_message if self.test else '',
            name=self.name,
            display_name=self.display_name,
            **self.__dict__)
