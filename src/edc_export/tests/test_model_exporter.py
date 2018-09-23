import csv

from django.test import TestCase, tag
from edc_pdutils import CsvModelExporter, ModelToDataframe
from tempfile import mkdtemp

from .helper import Helper
from .models import Crf, CrfEncrypted, SubjectVisit


class TestExport(TestCase):

    helper = Helper()

    def setUp(self):
        self.path = mkdtemp()
        for i in range(0, 5):
            self.helper.create_crf(i)
        self.subject_visit = SubjectVisit.objects.all()[0]

    def test_none(self):
        Crf.objects.all().delete()
        model = 'edc_export.crf'
        m = ModelToDataframe(model=model, add_columns_for='subject_visit')
        self.assertEqual(len(m.dataframe.index), 0)

    def test_records(self):
        model = 'edc_export.crf'
        m = ModelToDataframe(model=model, add_columns_for='subject_visit')
        self.assertEqual(len(m.dataframe.index), 5)
        model = 'edc_export.crfone'
        m = ModelToDataframe(model=model, add_columns_for='subject_visit')
        self.assertEqual(len(m.dataframe.index), 5)

    def test_records_as_qs(self):
        m = ModelToDataframe(queryset=Crf.objects.all(),
                             add_columns_for='subject_visit')
        self.assertEqual(len(m.dataframe.index), 5)

    def test_columns(self):
        model = 'edc_export.crf'
        m = ModelToDataframe(model=model, add_columns_for='subject_visit')
        self.assertEqual(len(list(m.dataframe.columns)), 26)

    def test_values(self):
        model = 'edc_export.crf'
        m = ModelToDataframe(model=model, add_columns_for='subject_visit')
        df = m.dataframe
        df.sort_values(['subject_identifier'], inplace=True)
        for i in range(0, 5):
            self.assertEqual(df.subject_identifier.iloc[i], f'12345{i}')
            self.assertEqual(df.visit_code.iloc[i], f'{i}000')

    def test_encrypted_none(self):
        model = 'edc_export.crfencrypted'
        m = ModelToDataframe(model=model, add_columns_for='subject_visit')
        self.assertEqual(len(m.dataframe.index), 0)

    def test_encrypted_records(self):
        CrfEncrypted.objects.create(
            subject_visit=self.subject_visit,
            encrypted1=f'encrypted1')
        model = 'edc_export.crfencrypted'
        m = ModelToDataframe(model=model, add_columns_for='subject_visit')
        self.assertEqual(len(m.dataframe.index), 1)

    def test_encrypted_records_as_qs(self):
        CrfEncrypted.objects.create(
            subject_visit=self.subject_visit,
            encrypted1=f'encrypted1')
        m = ModelToDataframe(
            queryset=CrfEncrypted.objects.all(), add_columns_for='subject_visit')
        self.assertEqual(len(m.dataframe.index), 1)

    def test_encrypted_to_csv_from_qs(self):
        CrfEncrypted.objects.create(
            subject_visit=self.subject_visit,
            encrypted1=f'encrypted1')
        model_exporter = CsvModelExporter(
            queryset=CrfEncrypted.objects.all(),
            add_columns_for='subject_visit',
            export_folder=self.path)
        model_exporter.to_csv()

    def test_encrypted_to_csv_from_model(self):
        CrfEncrypted.objects.create(
            subject_visit=self.subject_visit,
            encrypted1=f'encrypted1')
        model_exporter = CsvModelExporter(
            model='edc_export.CrfEncrypted',
            add_columns_for='subject_visit',
            export_folder=self.path)
        model_exporter.to_csv()

    def test_records_to_csv_from_qs(self):
        model_exporter = CsvModelExporter(
            queryset=Crf.objects.all(),
            add_columns_for='subject_visit',
            export_folder=self.path)
        model_exporter.to_csv()

    def test_records_to_csv_from_model(self):
        model_exporter = CsvModelExporter(
            model='edc_export.crf',
            add_columns_for='subject_visit',
            sort_by=['subject_identifier'],
            export_folder=self.path)
        exported = model_exporter.to_csv()
        with open(exported.path, 'r') as f:
            csv_reader = csv.DictReader(f, delimiter='|')
            rows = [row for row in enumerate(csv_reader)]
        self.assertEqual(len(rows), 5)
        for i in range(0, 5):
            self.assertEqual(rows[i][1].get('subject_identifier'), f'12345{i}')
            self.assertEqual(rows[i][1].get('visit_code'), f'{i}000')
