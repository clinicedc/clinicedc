import sys
import csv
import os

from django.apps import apps as django_apps
from django.test import TestCase, tag

from ..csv_exporters import CsvCrfTablesExporter, CsvCrfInlineTablesExporter
from ..csv_exporters import CsvNonCrfTablesExporter
from ..df_handlers import CrfDfHandler, NonCrfDfHandler
from .helper import Helper

app_config = django_apps.get_app_config('edc_pdutils')


class TestExport(TestCase):

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

    def test_crf_tables_to_csv_from_app_label_with_columns(self):

        class MyDfHandler(CrfDfHandler):
            visit_tbl = 'edc_pdutils_subjectvisit'
            registered_subject_tbl = 'edc_registration_registeredsubject'
            appointment_tbl = 'edc_appointment_appointment'

        class MyCsvCrfTablesExporter(CsvCrfTablesExporter):
            visit_column = 'subject_visit_id'
            df_handler_cls = MyDfHandler
            app_label = 'edc_pdutils'

        sys.stdout.write('\n')
        exporter = MyCsvCrfTablesExporter()
        exporter.to_csv()
        self.assertGreater(len(exporter.exported_paths), 0)
        for path in exporter.exported_paths.values():
            with open(path, 'r') as f:
                csv_reader = csv.DictReader(f, delimiter='|')
                rows = [row for row in enumerate(csv_reader)]
            self.assertGreater(len(rows), 0)

    def test_noncrf_tables_to_csv_from_app_label_with_columns(self):

        class MyDfHandler(NonCrfDfHandler):
            visit_tbl = 'edc_pdutils_subjectvisit'
            registered_subject_tbl = 'edc_registration_registeredsubject'
            appointment_tbl = 'edc_appointment_appointment'

        class MyNonCsvCrfTablesExporter(CsvNonCrfTablesExporter):
            visit_column = 'subject_visit_id'
            df_handler_cls = MyDfHandler
            app_label = 'edc_pdutils'

        sys.stdout.write('\n')
        exporter = MyNonCsvCrfTablesExporter()
        exporter.to_csv()
        self.assertGreater(len(exporter.exported_paths), 0)
        for path in exporter.exported_paths.values():
            with open(path, 'r') as f:
                csv_reader = csv.DictReader(f, delimiter='|')
                rows = [row for row in enumerate(csv_reader)]
            self.assertGreater(len(rows), 0)

    def test_export_inlines(self):

        class MyDfHandler(CrfDfHandler):
            visit_tbl = 'edc_pdutils_subjectvisit'
            registered_subject_tbl = 'edc_registration_registeredsubject'
            appointment_tbl = 'edc_appointment_appointment'

        class MyCsvCrfInlineTablesExporter(CsvCrfInlineTablesExporter):
            visit_column = 'subject_visit_id'
            df_handler_cls = MyDfHandler
            app_label = 'edc_pdutils'

        sys.stdout.write('\n')
        exporter = MyCsvCrfInlineTablesExporter()
        exporter.to_csv()
        self.assertGreater(len(exporter.exported_paths), 0)
        for path in exporter.exported_paths.values():
            with open(path, 'r') as f:
                csv_reader = csv.DictReader(f, delimiter='|')
                rows = [row for row in enumerate(csv_reader)]
            self.assertGreater(len(rows), 0)
