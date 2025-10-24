from datetime import datetime
from tempfile import mkdtemp
from zoneinfo import ZoneInfo

import time_machine
from clinicedc_tests.action_items import register_actions
from clinicedc_tests.consents import consent_v1
from clinicedc_tests.helper import Helper
from clinicedc_tests.models import CrfEncrypted, CrfFour, SubjectVisit
from clinicedc_tests.visit_schedules.visit_schedule_model_to_dataframe import (
    get_visit_schedule1,
)
from django.apps import apps as django_apps
from django.test import TestCase, override_settings, tag
from django.utils import timezone

from edc_consent.site_consents import site_consents
from edc_facility.import_holidays import import_holidays
from edc_model_to_dataframe.constants import SYSTEM_COLUMNS
from edc_model_to_dataframe.model_to_dataframe import ModelToDataframe
from edc_visit_schedule.site_visit_schedules import site_visit_schedules


@tag("model_to_dataframe")
@override_settings(
    EDC_EXPORT_EXPORT_FOLDER=mkdtemp(), EDC_EXPORT_UPLOAD_FOLDER=mkdtemp(), SITE_ID=10
)
@time_machine.travel(datetime(2025, 6, 11, 8, 00, tzinfo=ZoneInfo("UTC")))
class TestExport(TestCase):
    helper_cls = Helper

    def setUp(self):
        import_holidays()
        register_actions()
        site_consents.registry = {}
        site_consents.register(consent_v1)

        visit_schedule1 = get_visit_schedule1(consent_v1)
        site_visit_schedules._registry = {}
        site_visit_schedules.register(get_visit_schedule1(consent_v1))

        helper = self.helper_cls()
        for _ in range(0, 4):
            subject_visit = helper.enroll_to_baseline(
                visit_schedule_name=visit_schedule1.name,
                schedule_name="schedule1",
                report_datetime=timezone.now(),
            )
            helper.create_crfs(
                subject_visit, models=["clinicedc_tests.crffour", "clinicedc_tests.crffive"]
            )
            # CrfFour.objects.create(subject_visit=subject_visit)
        self.subject_visit = SubjectVisit.objects.all()[0]

    def test_none(self):
        CrfFour.objects.all().delete()
        model = "clinicedc_tests.crffour"
        m = ModelToDataframe(model=model)
        self.assertEqual(len(m.dataframe.index), 0)

    @tag("model_to_dataframe1")
    def test_records(self):
        model = "clinicedc_tests.crffour"
        m = ModelToDataframe(model=model)
        self.assertEqual(len(m.dataframe.index), 4)
        model = "clinicedc_tests.crffive"
        m = ModelToDataframe(model=model)
        self.assertEqual(len(m.dataframe.index), 4)

    def test_records_as_qs(self):
        m = ModelToDataframe(queryset=CrfFour.objects.all())
        self.assertEqual(len(m.dataframe.index), 4)

    def test_columns(self):
        model = "clinicedc_tests.crffour"

        fields = [f.attname for f in django_apps.get_model(model)._meta.get_fields()]
        fields.sort()

        # class drops system columns by default
        m = ModelToDataframe(model=model)
        for f in SYSTEM_COLUMNS:
            self.assertNotIn(f, m.dataframe.columns)

        # explicitly keep system columns
        m = ModelToDataframe(model=model, drop_sys_columns=False)
        for f in SYSTEM_COLUMNS:
            self.assertIn(f, m.dataframe.columns)

        # explicitly keep system columns and check all other fields
        # are there
        m = ModelToDataframe(model=model, drop_sys_columns=False)
        for f in fields:
            self.assertIn(f, m.dataframe.columns)

        # explicitly drop system columns
        m = ModelToDataframe(model=model, drop_sys_columns=True)
        for f in SYSTEM_COLUMNS:
            self.assertNotIn(f, m.dataframe.columns)

    def test_values(self):
        model = "clinicedc_tests.crffour"
        m = ModelToDataframe(model=model)
        df = m.dataframe
        df.sort_values(by=["subject_identifier", "visit_code"], inplace=True)
        for i, crf in enumerate(
            CrfFour.objects.all().order_by(
                "subject_visit__subject_identifier", "subject_visit__visit_code"
            )
        ):
            self.assertEqual(
                df.subject_identifier.iloc[i], crf.subject_visit.subject_identifier
            )
            self.assertEqual(df.visit_code.iloc[i], crf.subject_visit.visit_code)

    def test_encrypted_none(self):
        model = "clinicedc_tests.crfencrypted"
        m = ModelToDataframe(model=model)
        self.assertEqual(len(m.dataframe.index), 0)

    def test_encrypted_records(self):
        CrfEncrypted.objects.create(subject_visit=self.subject_visit, encrypted1="encrypted1")
        model = "clinicedc_tests.crfencrypted"
        m = ModelToDataframe(model=model)
        self.assertEqual(len(m.dataframe.index), 1)

    def test_encrypted_records_as_qs(self):
        CrfEncrypted.objects.create(subject_visit=self.subject_visit, encrypted1="encrypted1")
        m = ModelToDataframe(queryset=CrfEncrypted.objects.all())
        self.assertEqual(len(m.dataframe.index), 1)
