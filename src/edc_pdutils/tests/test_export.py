import os
import uuid
import pandas as pd

from django.apps import apps as django_apps
from django.test import TestCase
from edc_appointment.models import Appointment
from edc_base.utils import get_utcnow
from edc_registration.models import RegisteredSubject

from ..model_to_dataframe import ModelToDataframe
from .models import ListModel, SubjectVisit, Crf
from pprint import pprint
from edc_pdutils.tests.models import CrfEncrypted

app_config = django_apps.get_app_config('edc_pdutils')


class TestExport(TestCase):

    path = app_config.export_folder

    def setUp(self):
        for i in range(0, 5):
            subject_identifier = f'12345{i}'
            visit_code = f'{i}000'
            RegisteredSubject.objects.create(
                subject_identifier=subject_identifier)
            appointment = Appointment.objects.create(
                subject_identifier=subject_identifier,
                visit_code=visit_code,
                appt_datetime=get_utcnow())
            self.thing_one = ListModel.objects.create(
                name=f'thing_one_{i}', short_name=f'thing_one_{i}')
            self.thing_two = ListModel.objects.create(
                name=f'thing_two_{i}', short_name=f'thing_two_{i}')
            self.subject_visit = SubjectVisit.objects.create(
                appointment=appointment,
                subject_identifier=subject_identifier,
                report_datetime=get_utcnow())
            Crf.objects.create(
                subject_visit=self.subject_visit,
                char1=f'char{i}',
                date1=get_utcnow(),
                int1=i,
                uuid1=uuid.uuid4())

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

    def test_none(self):
        Crf.objects.all().delete()
        model = 'edc_pdutils.crf'
        m = ModelToDataframe(model=model, add_columns_for='subject_visit')
        self.assertEqual(len(m.dataframe.index), 0)

    def test_records(self):
        model = 'edc_pdutils.crf'
        m = ModelToDataframe(model=model, add_columns_for='subject_visit')
        self.assertEqual(len(m.dataframe.index), 5)

    def test_records_as_qs(self):
        m = ModelToDataframe(queryset=Crf.objects.all(),
                             add_columns_for='subject_visit')
        self.assertEqual(len(m.dataframe.index), 5)

    def test_columns(self):
        model = 'edc_pdutils.crf'
        m = ModelToDataframe(model=model, add_columns_for='subject_visit')
        self.assertEqual(len(list(m.dataframe.columns)), 18)

    def test_values(self):
        model = 'edc_pdutils.crf'
        m = ModelToDataframe(model=model, add_columns_for='subject_visit')
        df = m.dataframe
        for i in range(0, 5):
            self.assertEqual(df.subject_identifier[i], f'12345{i}')
            self.assertEqual(df.visit_code[i], f'{i}000')

    def test_encrypted_none(self):
        model = 'edc_pdutils.crfencrypted'
        m = ModelToDataframe(model=model, add_columns_for='subject_visit')
        self.assertEqual(len(m.dataframe.index), 0)

    def test_encrypted_records(self):
        CrfEncrypted.objects.create(
            subject_visit=self.subject_visit,
            encrypted1=f'encrypted1')
        model = 'edc_pdutils.crfencrypted'
        m = ModelToDataframe(model=model, add_columns_for='subject_visit')
        self.assertEqual(len(m.dataframe.index), 1)

    def test_encrypted_records_as_qs(self):
        CrfEncrypted.objects.create(
            subject_visit=self.subject_visit,
            encrypted1=f'encrypted1')
        m = ModelToDataframe(
            queryset=CrfEncrypted.objects.all(), add_columns_for='subject_visit')
        self.assertEqual(len(m.dataframe.index), 1)
