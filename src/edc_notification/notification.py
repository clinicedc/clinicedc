from django.conf import settings
from django.apps import apps as django_apps
from django.core import mail
from pprint import pprint
import inspect


class MailingList:

    def __init__(self, notification):
        self.list_email = notification.email_to
        self.display_name = notification.display_name

    def subscribe(self, email):
        print(
            f'{email} added to mailing list {self.list_email} for {self.display_name}.')

    def unsubscribe(self, email):
        print(
            f'{email} removed from mailing list {self.list_email} for {self.display_name}.')


class EmailMessage:

    def __init__(self, notification=None, instance=None, test=None, created=None):
        self.created = created
        self.instance = instance
        self.notification = notification
        self.test = test
        self.email_from = self.notification.email_from
        self.email_to = self.notification.email_to
        self.template_opts = {
            k: v or k.upper() for k, v in inspect.getmembers(self.notification)
            if not inspect.ismethod(v)
            and not k.startswith('_')
            and not inspect.isclass(v)
            and k not in self.__dict__}
        self.template_opts.update(
            updated='Update' if not created else '',
            subject_test_line=self.notification.subject_test_line if self.test else '',
            body_test_line=self.notification.body_test_line if self.test else '')
        self.subject = self.notification.subject_template.format(
            **self.template_opts,
            **self.__dict__)
        self.body = self.notification.body_template.format(
            **self.template_opts,
            **self.__dict__)

    def send(self):
        connection = mail.get_connection()
        args = [
            self.subject,
            self.body,
            self.email_from,
            self.email_to]
        email = mail.EmailMessage(*args, connection=connection)
        email.send()


class Notification:

    name = None
    display_name = None
    email_from = settings.EMAIL_CONTACTS.get('data_manager')
    email_to = None
    email_message_cls = EmailMessage
    mailing_list_cls = MailingList
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
        self.mailing_list = self.mailing_list_cls(self)
        self.email_to = self.email_to or [
            f'{self.name}.{settings.APP_NAME}@mg.clinicedc.org']
        self.protocol_name = django_apps.get_app_config(
            'edc_protocol').protocol_name

    def __str__(self):
        return f'{self.name}: {self.display_name}'

    def callback(self, instance=None, created=None, test=None, **kwargs):
        return False

    def notify(self, **kwargs):
        if self.callback(**kwargs):
            email_message = self.email_message_cls(notification=self, **kwargs)
            email_message.send()
