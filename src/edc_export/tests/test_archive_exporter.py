import os
import shutil

from django.contrib.auth.models import User
from django.test import TestCase, tag
from django.test.utils import override_settings
from edc_registration.models import RegisteredSubject
from tempfile import mkdtemp

from ..archive_exporter import ArchiveExporter, ArchiveExporterNothingExported


@override_settings(EXPORT_FOLDER=mkdtemp())
class TestArchiveExporter(TestCase):

    def setUp(self):

        self.user = User.objects.create(username='erikvw')
        RegisteredSubject.objects.create(subject_identifier='12345')
        self.models = [
            'auth.user',
            'edc_registration.registeredsubject']

    def test_request_archive(self):

        exporter = ArchiveExporter(
            models=self.models,
            user=self.user,
            archive=True)
        folder = mkdtemp()
        shutil.unpack_archive(
            exporter.archive_filename, folder, 'zip')
        filenames = os.listdir(folder)
        self.assertGreater(
            len([f for f in filenames]), 0)

    def test_request_archive_filename_exists(self):

        exporter = ArchiveExporter(
            models=self.models, user=self.user, archive=True)
        filename = exporter.archive_filename
        self.assertIsNotNone(filename)
        self.assertTrue(
            os.path.exists(filename),
            msg=f'file \'{filename}\' does not exist')

    def test_requested_with_invalid_table(self):
        models = [
            'auth.blah',
            'edc_registration.registeredsubject']
        self.assertRaises(
            LookupError, ArchiveExporter,
            models=models, user=self.user, archive=True)

    def test_requested_with_nothing(self):
        self.assertRaises(
            ArchiveExporterNothingExported, ArchiveExporter,
            models=[], user=self.user, archive=True)
