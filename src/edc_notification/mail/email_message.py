import inspect

from django.core import mail


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
