import csv
import sys

from django.apps import apps as django_apps
from django.test import TestCase, tag
from tempfile import mkdtemp

from ..csv_exporters import CsvNonCrfTablesExporter
from ..df_handlers import NonCrfDfHandler
from .helper import Helper

app_config = django_apps.get_app_config('edc_pdutils')


class TestExport(TestCase):

    helper = Helper()

    def setUp(self):
        self.path = mkdtemp()
        for i in range(0, 5):
            self.helper.create_crf(i)

    def test_noncrf_tables_to_csv_from_app_label_with_columns(self):

        class MyDfHandler(NonCrfDfHandler):
            visit_tbl = 'edc_pdutils_subjectvisit'
            registered_subject_tbl = 'edc_registration_registeredsubject'
            appointment_tbl = 'edc_appointment_appointment'

        class MyNonCsvCrfTablesExporter(CsvNonCrfTablesExporter):
            without_visit_columns = ['subject_visit_id']
            df_handler_cls = MyDfHandler
            app_label = 'edc_pdutils'
            export_folder = self.path

        sys.stdout.write('\n')
        exporter = MyNonCsvCrfTablesExporter()
        exporter.to_csv()
        self.assertGreater(len(exporter.exported_paths), 0)
        for path in exporter.exported_paths.values():
            with open(path, 'r') as f:
                csv_reader = csv.DictReader(f, delimiter='|')
                rows = [row for row in enumerate(csv_reader)]
            self.assertGreater(len(rows), 0)
