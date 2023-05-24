import csv
from tempfile import mkdtemp

from django.test import TestCase, override_settings
from edc_appointment.models import Appointment
from edc_facility.import_holidays import import_holidays
from edc_pdutils import CsvModelExporter, ModelToDataframe
from edc_visit_schedule.site_visit_schedules import site_visit_schedules

from ...utils import get_export_folder
from ..helper import Helper
from ..models import Crf, CrfEncrypted, SubjectVisit
from ..visit_schedule import visit_schedule1


@override_settings(EDC_EXPORT_EXPORT_FOLDER=mkdtemp(), EDC_EXPORT_UPLOAD_FOLDER=mkdtemp())
class TestExport(TestCase):
    def setUp(self):
        import_holidays()
        self.helper = Helper()
        site_visit_schedules._registry = {}
        site_visit_schedules.register(visit_schedule1)
        self.helper.create_crfs(5)
        self.subject_visit = SubjectVisit.objects.all()[0]

    def test_none(self):
        Crf.objects.all().delete()
        model = "edc_export.crf"
        m = ModelToDataframe(model=model)
        self.assertEqual(len(m.dataframe.index), 0)

    def test_records(self):
        model = "edc_export.crf"
        m = ModelToDataframe(model=model)
        self.assertEqual(len(m.dataframe.index), 4)
        model = "edc_export.crfone"
        m = ModelToDataframe(model=model)
        self.assertEqual(len(m.dataframe.index), 4)

    def test_records_as_qs(self):
        m = ModelToDataframe(queryset=Crf.objects.all())
        self.assertEqual(len(m.dataframe.index), 4)

    def test_columns(self):
        model = "edc_export.crf"
        m = ModelToDataframe(model=model, drop_sys_columns=False)
        self.assertEqual(len(list(m.dataframe.columns)), 26)

    def test_values(self):
        model = "edc_export.crf"
        m = ModelToDataframe(model=model)
        df = m.dataframe
        df.sort_values(by=["subject_identifier", "visit_code"], inplace=True)
        for i, appointment in enumerate(
            Appointment.objects.all().order_by("subject_identifier", "visit_code")
        ):
            self.assertEqual(df.subject_identifier.iloc[i], appointment.subject_identifier)
            self.assertEqual(df.visit_code.iloc[i], appointment.visit_code)

    def test_encrypted_none(self):
        model = "edc_export.crfencrypted"
        m = ModelToDataframe(model=model)
        self.assertEqual(len(m.dataframe.index), 0)

    def test_encrypted_records(self):
        CrfEncrypted.objects.create(subject_visit=self.subject_visit, encrypted1="encrypted1")
        model = "edc_export.crfencrypted"
        m = ModelToDataframe(model=model)
        self.assertEqual(len(m.dataframe.index), 1)

    def test_encrypted_records_as_qs(self):
        CrfEncrypted.objects.create(subject_visit=self.subject_visit, encrypted1="encrypted1")
        m = ModelToDataframe(queryset=CrfEncrypted.objects.all())
        self.assertEqual(len(m.dataframe.index), 1)

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
            model="edc_export.CrfEncrypted",
            export_folder=get_export_folder(),
        )
        model_exporter.to_csv()

    def test_records_to_csv_from_qs(self):
        model_exporter = CsvModelExporter(
            queryset=Crf.objects.all(), export_folder=get_export_folder()
        )
        model_exporter.to_csv()

    def test_records_to_csv_from_model(self):
        model_exporter = CsvModelExporter(
            model="edc_export.crf",
            sort_by=["subject_identifier", "visit_code"],
            export_folder=get_export_folder(),
        )
        exported = model_exporter.to_csv()
        with open(exported.path, "r") as f:
            csv_reader = csv.DictReader(f, delimiter="|")
            rows = [row for row in enumerate(csv_reader)]
        self.assertEqual(len(rows), 4)
        for i, appointment in enumerate(
            Appointment.objects.all().order_by("subject_identifier", "visit_code")
        ):
            self.assertEqual(
                rows[i][1].get("subject_identifier"), appointment.subject_identifier
            )
            self.assertEqual(rows[i][1].get("visit_code"), appointment.visit_code)
