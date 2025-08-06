from tempfile import mkdtemp

from django.apps import apps as django_apps
from django.test import TestCase, override_settings
from edc_facility.import_holidays import import_holidays
from edc_utils import get_utcnow
from edc_visit_schedule.site_visit_schedules import site_visit_schedules

from edc_model_to_dataframe import ModelToDataframe
from model_to_dataframe_app.models import Crf, CrfEncrypted, SubjectVisit
from model_to_dataframe_app.visit_schedule import visit_schedule1

from ...constants import SYSTEM_COLUMNS
from ..create_crfs import create_crfs
from ..helper import Helper


@override_settings(EDC_EXPORT_EXPORT_FOLDER=mkdtemp(), EDC_EXPORT_UPLOAD_FOLDER=mkdtemp())
class TestExport(TestCase):
    helper_cls = Helper

    def setUp(self):
        import_holidays()
        site_visit_schedules._registry = {}
        site_visit_schedules.register(visit_schedule1)
        for i in range(0, 7):
            helper = self.helper_cls(subject_identifier=f"subject-{i}")
            helper.consent_and_put_on_schedule(
                visit_schedule_name=visit_schedule1.name,
                schedule_name="schedule1",
                report_datetime=get_utcnow(),
            )
        create_crfs(5)
        self.subject_visit = SubjectVisit.objects.all()[0]

    def test_none(self):
        Crf.objects.all().delete()
        model = "model_to_dataframe_app.crf"
        m = ModelToDataframe(model=model)
        self.assertEqual(len(m.dataframe.index), 0)

    def test_records(self):
        model = "model_to_dataframe_app.crf"
        m = ModelToDataframe(model=model)
        self.assertEqual(len(m.dataframe.index), 4)
        model = "model_to_dataframe_app.crfone"
        m = ModelToDataframe(model=model)
        self.assertEqual(len(m.dataframe.index), 4)

    def test_records_as_qs(self):
        m = ModelToDataframe(queryset=Crf.objects.all())
        self.assertEqual(len(m.dataframe.index), 4)

    def test_columns(self):
        model = "model_to_dataframe_app.crf"

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
        model = "model_to_dataframe_app.crf"
        m = ModelToDataframe(model=model)
        df = m.dataframe
        df.sort_values(by=["subject_identifier", "visit_code"], inplace=True)
        for i, crf in enumerate(
            Crf.objects.all().order_by(
                "subject_visit__subject_identifier", "subject_visit__visit_code"
            )
        ):
            self.assertEqual(
                df.subject_identifier.iloc[i], crf.subject_visit.subject_identifier
            )
            self.assertEqual(df.visit_code.iloc[i], crf.subject_visit.visit_code)

    def test_encrypted_none(self):
        model = "model_to_dataframe_app.crfencrypted"
        m = ModelToDataframe(model=model)
        self.assertEqual(len(m.dataframe.index), 0)

    def test_encrypted_records(self):
        CrfEncrypted.objects.create(subject_visit=self.subject_visit, encrypted1="encrypted1")
        model = "model_to_dataframe_app.crfencrypted"
        m = ModelToDataframe(model=model)
        self.assertEqual(len(m.dataframe.index), 1)

    def test_encrypted_records_as_qs(self):
        CrfEncrypted.objects.create(subject_visit=self.subject_visit, encrypted1="encrypted1")
        m = ModelToDataframe(queryset=CrfEncrypted.objects.all())
        self.assertEqual(len(m.dataframe.index), 1)
