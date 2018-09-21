import os
import shutil
import sys

from datetime import datetime
from django.apps import apps as django_apps
from django.conf import settings
from django.core.mail.message import EmailMessage
from edc_base.utils import get_utcnow
from tempfile import mkdtemp

from .csv_exporters import CsvModelExporter


class NothingToExport(Exception):
    pass


class FilesEmailer:

    def __init__(self, path=None, user=None, export_history=None):
        from django.contrib.auth.models import User
        self.user = User.objects.get(username=user)
        self.path = path
        self.email_files()
        export_history.emailed_to = self.user.email
        export_history.emailed_datetime = get_utcnow()
        export_history.save()

    def get_email_message(self):
        body = [
            f'Hello {self.user.first_name or self.user.username}',
            f'The data you requested is attached.',
            (f'An email can contain no more than 10 attached files. If you selected \n'
             f'more than 10 tables for export, you will receive more than one email for \n'
             f'this request.'),
            (f'Tables with zero records are not exported so the total number of attached \n'
             f'files may be fewer than the number of tables you originally selected.'),
            (f'When importing files into your software note that the data are delimited \n'
             f'by a "|" instead of a comma. You will need to indicate this when you \n'
             f'open/import the files into Excel, Numbers or whichever software you are using.'),
            # f'{summary}',
            f'Thanks'
        ]
        return EmailMessage(
            subject='Ambition trial data request',
            body='\n\n'.join(body),
            from_email='data-request@mg.clinicedc.org',
            to=[self.user.email])

    def email_files(self):
        email_message = self.get_email_message()
        files = []
        for filename in os.listdir(self.path):
            if os.path.splitext(filename)[1] == '.csv':
                files.append(os.path.join(self.path, filename))
        x = 0
        for index, file in enumerate(files):
            email_message.attach_file(file)
            x += 1
            if x >= 10:
                email_message.subject = (
                    f'{email_message.subject} (items '
                    f'{index + 2 - x}-{index + 1} of {len(files)})')
                email_message.send()
                email_message = self.get_email_message()
                x = 0
        if x > 0:
            email_message.subject = (
                f'{email_message.subject} (items '
                f'{index + 2 - x}-{index + 1} of {len(files)})')
            email_message.send()
        sys.stdout.write(
            f'\nEmailed export files to {self.user.email}.\n')


class ArchiveExporter:

    """Exports a list of models to individual CSV files and
    adds each to a single zip archive.
    """

    date_format = '%Y%m%d%H%M%S'
    data_request_model = 'edc_pdutils.datarequest'
    export_history_model = 'edc_pdutils.datarequesthistory'
    csv_exporter_cls = CsvModelExporter
    files_emailer_cls = FilesEmailer

    def __init__(self, export_folder=None, date_format=None, email_to_user=None):
        self.date_format = date_format or self.date_format
        self.export_folder = export_folder or settings.EXPORT_FOLDER
        self.email_to_user = email_to_user

    def export_to_archive(self, data_request=None, name=None,
                          models=None, decrypt=None, user=None, **kwargs):
        """Returns a history model instance after exporting
         models to a single zip archive file.

        models: a list of model names in label_lower format.
        """
        if data_request:
            models = data_request.requested_as_list
            decrypt = data_request.decrypt
            user = data_request.user_created
        else:
            timestamp = datetime.now().strftime('%Y%m%d%H%M')
            data_request = django_apps.get_model(
                self.data_request_model).objects.create(
                name=name or f'Data request {timestamp}',
                models='\n'.join(models),
                decrypt=False if decrypt is None else decrypt)
        exported = []
        tmp_folder = mkdtemp()
        user = user or 'unknown_user'
        for model in models:
            csv_exporter = self.csv_exporter_cls(
                model=model,
                export_folder=tmp_folder,
                decrypt=decrypt, **kwargs)
            exported.append(csv_exporter.to_csv())
        if not exported:
            raise NothingToExport(
                f'Nothing exported. Got models={models}.')
        else:
            summary = [x for x in str(exported)]
            summary.sort()
            export_history = django_apps.get_model(
                self.export_history_model).objects.create(
                data_request=data_request,
                exported_datetime=get_utcnow(),
                summary='\n'.join(summary),
                user_created=user)
            if self.email_to_user:
                self.files_emailer_cls(
                    path=tmp_folder,
                    user=user,
                    export_history=export_history)
            else:
                archive_filename = self._archive(
                    tmp_folder=tmp_folder, user=user)
                export_history.archive_filename = archive_filename
                export_history.save()
                sys.stdout.write(
                    f'\nExported archive to {export_history.archive_filename}.\n')
        return export_history

    def _archive(self, tmp_folder=None, exported_datetime=None, user=None):
        """Returns the archive zip filename after calling make_archive.
        """
        exported_datetime = exported_datetime or get_utcnow()
        formatted_date = exported_datetime.strftime(self.date_format)
        export_folder = tmp_folder if self.email_to_user else self.export_folder
        return shutil.make_archive(
            os.path.join(export_folder, f'{user}_{formatted_date}'), 'zip', tmp_folder)
