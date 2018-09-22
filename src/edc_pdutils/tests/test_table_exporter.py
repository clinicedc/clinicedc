import csv
import os
import sys

from django.apps import apps as django_apps
from django.test import TestCase, tag

from ..csv_exporters import CsvTablesExporter
from .helper import Helper


@tag('1')
class TestExport(TestCase):

    app_config = django_apps.get_app_config('edc_pdutils')
    path = app_config.export_folder
    helper = Helper()

    def setUp(self):
        for i in range(0, 5):
            self.helper.create_crf(i)

    def tearDown(self):
        """Remove .csv files created in tests.
        """
        super().tearDown()
        if 'edc_pdutils' not in self.path:
            raise ValueError(f'Invalid path in test. Got {self.path}')
        files = os.listdir(self.path)
        for file in files:
            if '.csv' in file:
                file = os.path.join(self.path, file)
                os.remove(file)

    def test_tables_to_csv_lower_columns(self):
        sys.stdout.write('\n')
        tables_exporter = CsvTablesExporter(app_label='edc_pdutils')
        for path in tables_exporter.exported_paths.values():
            with open(path, 'r') as f:
                csv_reader = csv.DictReader(f, delimiter='|')
                for row in csv_reader:
                    for field in row:
                        self.assertEqual(field.lower(), field)
                    break

    def test_tables_to_csv_from_app_label(self):
        sys.stdout.write('\n')
        tables_exporter = CsvTablesExporter(app_label='edc_pdutils')
        for path in tables_exporter.exported_paths.values():
            with open(path, 'r') as f:
                csv_reader = csv.DictReader(f, delimiter='|')
                rows = [row for row in enumerate(csv_reader)]
            self.assertGreater(len(rows), 0)

    def test_tables_to_csv_from_app_label_exclude_history(self):

        class MyCsvTablesExporter(CsvTablesExporter):
            exclude_history_tables = True

        sys.stdout.write('\n')
        tables_exporter = MyCsvTablesExporter(app_label='edc_pdutils')
        for path in tables_exporter.exported_paths:
            self.assertNotIn('history', path)
