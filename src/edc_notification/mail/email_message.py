import inspect

from django.conf import settings
from django.core import mail


class EmailMessage:

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
        '{subject_test_line}{protocol_name}: '
        '{display_name} '
        'for {instance.subject_identifier}')
    body_test_line = 'THIS IS A TEST MESSAGE. NO ACTION IS REQUIRED\n\n'
    subject_test_line = 'TEST/UAT -- '

    def __init__(self, notification=None, instance=None, **kwargs):
        self.instance = instance
        self.notification = notification
        try:
            self.live_system = settings.LIVE_SYSTEM
        except AttributeError:
            self.live_system = False
        self.test = not self.live_system
        self.email_from = self.notification.email_from
        self.email_to = self.notification.email_to
        self.template_opts = {
            k: v or k.upper() for k, v in inspect.getmembers(self.notification)
            if not inspect.ismethod(v)
            and not k.startswith('_')
            and not inspect.isclass(v)
            and k not in self.__dict__}
        self.template_opts.update(
            subject_test_line=self.get_subject_test_line(),
            body_test_line=self.get_body_test_line())
        self.subject = self.get_subject_template().format(
            **self.template_opts,
            **self.__dict__)
        self.body = self.get_body_template().format(
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

    def get_body_template(self):
        return self.notification.body_template or self.body_template

    def get_subject_template(self):
        return self.notification.subject_template or self.subject_template

    def get_body_test_line(self):
        if self.live_system:
            return self.notification.body_test_line or self.body_test_line
        return ''

    def get_subject_test_line(self):
        if self.live_system:
            return self.notification.subject_test_line or self.subject_test_line
        return ''
