import os
import shutil

from django.contrib.auth.models import User
from django.test import TestCase, tag
from django.test.utils import override_settings
from edc_registration.models import RegisteredSubject
from tempfile import mkdtemp

from ..archive_exporter import ArchiveExporter, NothingToExport


@override_settings(EXPORT_FOLDER=mkdtemp())
class TestArchiveExporter(TestCase):

    def setUp(self):

        self.user = User.objects.create(username='erikvw')
        RegisteredSubject.objects.create(subject_identifier='12345')
        self.models = [
            'auth.user',
            'edc_registration.registeredsubject']

    def test_request_archive(self):

        exporter = ArchiveExporter()
        export_history = exporter.export_to_archive(
            models=self.models,
            user=self.user)
        folder = mkdtemp()
        shutil.unpack_archive(
            export_history.archive_filename, folder, 'zip')
        filenames = os.listdir(folder)
        self.assertGreater(
            len([f for f in filenames]), 0)

    def test_request_archive_filename_exists(self):

        exporter = ArchiveExporter()
        history = exporter.export_to_archive(
            models=self.models, user=self.user)
        filename = history.archive_filename
        self.assertIsNotNone(filename)
        self.assertTrue(
            os.path.exists(filename),
            msg=f'file \'{filename}\' does not exist')

    def test_requested_with_invalid_table(self):
        models = [
            'auth.blah',
            'edc_registration.registeredsubject']
        exporter = ArchiveExporter()
        self.assertRaises(
            LookupError, exporter.export_to_archive,
            models=models, user=self.user)

    def test_requested_with_nothing(self):
        models = []
        exporter = ArchiveExporter()
        self.assertRaises(
            NothingToExport, exporter.export_to_archive,
            models=models, user=self.user)
