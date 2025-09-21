import csv
from datetime import datetime
from tempfile import mkdtemp
from zoneinfo import ZoneInfo

import time_machine
from clinicedc_tests.consents import consent_v1
from clinicedc_tests.helper import Helper
from clinicedc_tests.models import Crf, CrfEncrypted, CrfThree, SubjectVisit
from clinicedc_tests.sites import all_sites
from clinicedc_tests.visit_schedules.visit_schedule import get_visit_schedule
from django.test import TestCase, override_settings, tag
from django.utils import timezone

from edc_consent import site_consents
from edc_export.utils import get_export_folder
from edc_facility.import_holidays import import_holidays
from edc_pdutils.df_exporters import CsvModelExporter
from edc_sites.site import sites as site_sites
from edc_sites.utils import add_or_update_django_sites
from edc_visit_schedule.site_visit_schedules import site_visit_schedules

utc_tz = ZoneInfo("UTC")


@tag("export")
@override_settings(
    EDC_EXPORT_EXPORT_FOLDER=mkdtemp(), EDC_EXPORT_UPLOAD_FOLDER=mkdtemp(), SITE_ID=10
)
@time_machine.travel(datetime(2025, 6, 11, 8, 00, tzinfo=utc_tz))
class TestExport(TestCase):
    @classmethod
    def setUpTestData(cls):
        import_holidays()
        site_sites._registry = {}
        site_sites.loaded = False
        site_sites.register(*all_sites)
        add_or_update_django_sites()

    def setUp(self):
        helper = Helper()
        site_consents.registry = {}
        site_consents.register(consent_v1)
        visit_schedule = get_visit_schedule(consent_v1)
        site_visit_schedules._registry = {}
        site_visit_schedules.register(visit_schedule)
        for _ in range(0, 7):
            subject_visit = helper.enroll_to_baseline(
                visit_schedule_name=visit_schedule.name,
                schedule_name="schedule",
                report_datetime=timezone.now(),
            )
            helper.create_crfs(subject_visit)
        self.subject_visit = SubjectVisit.objects.all()[0]

    def test_encrypted_to_csv_from_qs(self):
        CrfEncrypted.objects.create(subject_visit=self.subject_visit, encrypted1="encrypted1")
        model_exporter = CsvModelExporter(
            queryset=CrfEncrypted.objects.all(),
            export_folder=get_export_folder(),
        )
        model_exporter.to_csv()

    def test_encrypted_to_csv_from_model(self):
        CrfEncrypted.objects.create(subject_visit=self.subject_visit, encrypted1="encrypted1")
        model_exporter = CsvModelExporter(
            model="clinicedc_tests.CrfEncrypted",
            export_folder=get_export_folder(),
        )
        model_exporter.to_csv()

    def test_records_to_csv_from_qs(self):
        model_exporter = CsvModelExporter(
            queryset=CrfThree.objects.all(), export_folder=get_export_folder()
        )
        model_exporter.to_csv()

    def test_records_to_csv_from_model(self):
        model_exporter = CsvModelExporter(
            model="clinicedc_tests.crfone",
            sort_by=["subject_identifier", "visit_code"],
            export_folder=get_export_folder(),
        )
        exported = model_exporter.to_csv()
        with exported.path.open() as f:
            csv_reader = csv.DictReader(f, delimiter="|")
            rows = [row for row in enumerate(csv_reader)]
        self.assertEqual(len(rows), 7)
        for i, crf in enumerate(
            Crf.objects.all().order_by(
                "subject_visit__subject_identifier", "subject_visit__visit_code"
            )
        ):
            self.assertEqual(
                rows[i][1].get("subject_identifier"),
                crf.subject_visit.subject_identifier,
            )
            self.assertEqual(rows[i][1].get("visit_code"), crf.subject_visit.visit_code)
