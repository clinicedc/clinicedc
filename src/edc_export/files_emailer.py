import os
import socket
import sys

from django.core.exceptions import ValidationError
from django.core.mail.message import EmailMessage


class FilesEmailerError(ValidationError):
    pass


class FilesEmailer:

    def __init__(self, path=None, user=None, file_ext=None, summary=None,
                 verbose=None):
        self.file_ext = file_ext or '.csv'
        self.user = user
        self.path = path
        self.summary = summary
        self.verbose = verbose
        self.email_files()

    def get_email_message(self):
        body = [
            f'Hello {self.user.first_name or self.user.username}',
            f'The data you requested are attached.',
            (f'An email can contain no more than 10 attached files. If you selected \n'
             f'more than 10 tables for export, you will receive more than one email for \n'
             f'this request.'),
            (f'Tables with zero records are not exported so the total number of attached \n'
             f'files may be fewer than the number of tables you originally selected.'),
            (f'When importing files into your software note that the data are delimited \n'
             f'by a pipe, "|",  instead of a comma. You will need to indicate this when you \n'  # noqa
             f'open/import the files into Excel, Numbers or whichever software '
             f'you are using.'),
            f'Your request includes the following data:',
            f'{self.summary}',
            f'Thanks'
        ]
        return EmailMessage(
            subject='Ambition trial data request',
            body='\n\n'.join(body),
            from_email='data-request@mg.clinicedc.org',
            to=[self.user.email])

    def send(self, email_message):
        try:
            email_message.send()
        except socket.gaierror:
            raise FilesEmailerError(
                'Unable to connect to email server.',
                code='gaierror')

    def email_files(self):
        email_message = self.get_email_message()
        files = []
        for filename in os.listdir(self.path):
            if os.path.splitext(filename)[1] == self.file_ext:
                files.append(os.path.join(self.path, filename))
        x = 0
        for index, file in enumerate(files):
            email_message.attach_file(file)
            x += 1
            if x >= 10:
                email_message.subject = (
                    f'{email_message.subject} (items '
                    f'{index + 2 - x}-{index + 1} of {len(files)})')
                self.send(email_message)
                email_message = self.get_email_message()
                x = 0
        if x > 0:
            email_message.subject = (
                f'{email_message.subject} (items '
                f'{index + 2 - x}-{index + 1} of {len(files)})')
            self.send(email_message)
        if self.verbose:
            sys.stdout.write(
                f'\nEmailed export files to {self.user.email}.\n')
