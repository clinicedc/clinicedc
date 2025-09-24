import csv
import uuid
from tempfile import mkdtemp
from time import sleep
from unittest.case import skip

from clinicedc_tests.consents import consent_v1
from clinicedc_tests.helper import Helper
from clinicedc_tests.models import Crf, CrfEncrypted, CrfThree, ListModel, SubjectVisit
from clinicedc_tests.sites import all_sites
from clinicedc_tests.visit_schedules.visit_schedule import get_visit_schedule
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase, override_settings
from django.utils import timezone

from edc_consent import site_consents
from edc_export.constants import EXPORTED, INSERT, UPDATE
from edc_export.model_exporter import ModelExporter, ValueGetterInvalidLookup
from edc_export.models import FileHistory, ObjectHistory
from edc_facility.import_holidays import import_holidays
from edc_sites.site import sites as site_sites
from edc_sites.utils import add_or_update_django_sites
from edc_visit_schedule.site_visit_schedules import site_visit_schedules


@skip("not used")
@override_settings(
    EDC_EXPORT_EXPORT_FOLDER=mkdtemp(), EDC_EXPORT_UPLOAD_FOLDER=mkdtemp(), SITE_ID=10
)
class TestExportModel(TestCase):
    @classmethod
    def setUpTestData(cls):
        import_holidays()
        site_sites._registry = {}
        site_sites.loaded = False
        site_sites.register(*all_sites)
        add_or_update_django_sites()
        site_consents.registry = {}
        site_consents.register(consent_v1)
        site_visit_schedules._registry = {}
        visit_schedule = get_visit_schedule(consent_v1)
        site_visit_schedules.register(get_visit_schedule(consent_v1))
        for _ in range(0, 7):
            helper = Helper()
            helper.enroll_to_baseline(
                visit_schedule_name=visit_schedule.name,
                schedule_name="schedule",
                report_datetime=timezone.now(),
            )

    def setUp(self):
        self.subject_visit = SubjectVisit.objects.all()[0]
        self.thing_one = ListModel.objects.create(display_name="thing_one", name="thing_one")
        self.thing_two = ListModel.objects.create(display_name="thing_two", name="thing_two")
        self.crf = CrfThree.objects.create(
            subject_visit=self.subject_visit,
            f1="char",
            appt_date=timezone.now(),
            f4=1,
            f5=uuid.uuid4(),
        )

    def test_model(self):
        ModelExporter(
            model="export_app.crf",
            lookups={"subject_identifier": "subject_visit__subject_identifier"},
        )

    def test_queryset_no_data(self):
        Crf.objects.all().delete()
        queryset = Crf.objects.all()
        self.assertEqual(queryset.model, Crf)
        ModelExporter(queryset=queryset)

    def test_export_file(self):
        """Assert creates file."""
        Crf.objects.all().delete()
        queryset = Crf.objects.all()
        self.assertEqual(queryset.model, Crf)
        model_exporter = ModelExporter(
            queryset=queryset,
            lookups={"subject_identifier": "subject_visit__subject_identifier"},
        )
        path = model_exporter.export()
        self.assertTrue(path.exists())
        self.assertIn("export_app_crf_", str(path))

    def test_field_names(self):
        Crf.objects.all().delete()
        queryset = Crf.objects.all()
        self.assertEqual(queryset.model, Crf)
        model_exporter = ModelExporter(
            queryset=queryset,
            lookups={"subject_identifier": "subject_visit__subject_identifier"},
        )
        self.assertIn("f1", model_exporter.field_names)
        self.assertIn("appt_date", model_exporter.field_names)
        self.assertIn("f4", model_exporter.field_names)
        self.assertIn("f5", model_exporter.field_names)
        self.assertIn("m2m", model_exporter.field_names)
        for i, name in enumerate(model_exporter.export_fields):
            self.assertEqual(name, model_exporter.field_names[i])
        model_exporter.field_names.reverse()
        model_exporter.audit_fields.reverse()
        for i, name in enumerate(model_exporter.audit_fields):
            self.assertEqual(name, model_exporter.field_names[i])

    def test_field_names_with_excluded(self):
        Crf.objects.all().delete()
        queryset = Crf.objects.all()
        model_exporter = ModelExporter(
            queryset=queryset,
            exclude_field_names=["appt_date", "f5"],
            lookups={"subject_identifier": "subject_visit__subject_identifier"},
        )
        self.assertIn("f1", model_exporter.field_names)
        self.assertNotIn("appt_date", model_exporter.field_names)
        self.assertIn("f4", model_exporter.field_names)
        self.assertNotIn("f5", model_exporter.field_names)
        self.assertIn("m2m", model_exporter.field_names)
        for i, name in enumerate(model_exporter.export_fields):
            self.assertEqual(name, model_exporter.field_names[i])
        model_exporter.field_names.reverse()
        model_exporter.audit_fields.reverse()
        for i, name in enumerate(model_exporter.audit_fields):
            self.assertEqual(name, model_exporter.field_names[i])

    def test_field_names_provided(self):
        Crf.objects.all().delete()
        queryset = Crf.objects.all()
        model_exporter = ModelExporter(
            queryset=queryset,
            field_names=["f1"],
            lookups={"subject_identifier": "subject_visit__subject_identifier"},
        )
        self.assertIn("f1", model_exporter.field_names)
        self.assertNotIn("appt_date", model_exporter.field_names)
        self.assertNotIn("f4", model_exporter.field_names)
        self.assertNotIn("f5", model_exporter.field_names)
        self.assertNotIn("m2m", model_exporter.field_names)
        for i, name in enumerate(model_exporter.export_fields):
            self.assertEqual(name, model_exporter.field_names[i])
        model_exporter.field_names.reverse()
        model_exporter.audit_fields.reverse()
        for i, name in enumerate(model_exporter.audit_fields):
            self.assertEqual(name, model_exporter.field_names[i])

    def test_with_queryset(self):
        queryset = Crf.objects.all()
        model_exporter = ModelExporter(
            queryset=queryset,
            lookups={"subject_identifier": "subject_visit__subject_identifier"},
        )
        path = model_exporter.export()
        with path.open() as f:
            csv_reader = csv.reader(f)
            rows = [row for row in enumerate(csv_reader)]
            self.assertEqual(len(rows), 2)

    def test_header_row(self):
        queryset = Crf.objects.all()
        model_exporter = ModelExporter(
            queryset=queryset,
            lookups={
                "subject_visit": "subject_visit__report_datetime",
                "subject_identifier": "subject_visit__subject_identifier",
            },
        )
        path = model_exporter.export()
        with path.open() as f:
            csv_reader = csv.reader(f)
            rows = [row for row in enumerate(csv_reader)]
        header = rows[0][1][0]
        self.assertEqual(model_exporter.field_names, header.split("|"))

    def test_values_row(self):
        queryset = Crf.objects.all()
        model_exporter = ModelExporter(
            queryset=queryset,
            lookups={
                "subject_visit": "subject_visit__report_datetime",
                "subject_identifier": "subject_visit__subject_identifier",
            },
        )
        path = model_exporter.export()
        with path.open() as f:
            csv_reader = csv.reader(f)
            rows = [row for row in enumerate(csv_reader)]
        values_row = rows[1][1][0]
        self.assertEqual(len(values_row.split("|")), 31)

    def test_lookup(self):
        queryset = Crf.objects.all()
        model_exporter = ModelExporter(
            queryset=queryset,
            lookups={
                "subject_visit": "subject_visit__report_datetime",
                "subject_identifier": "subject_visit__subject_identifier",
            },
        )
        self.assertTrue(model_exporter.export())

    def test_invalid_lookup_raises(self):
        queryset = Crf.objects.all()
        model_exporter = ModelExporter(
            queryset=queryset, lookups={"subject_identifier": "subject_visit__blah"}
        )
        self.assertRaises(ValueGetterInvalidLookup, model_exporter.export)

    def test_m2m(self):
        self.crf.m2m.add(self.thing_one)
        self.crf.m2m.add(self.thing_two)
        queryset = Crf.objects.all()
        model_exporter = ModelExporter(
            queryset=queryset,
            lookups={"subject_identifier": "subject_visit__subject_identifier"},
        )
        path = model_exporter.export()
        with path.open() as f:
            csv_reader = csv.reader(f)
            rows = [row for row in enumerate(csv_reader)]
        values_row = rows[1][1][0]
        self.assertIn("thing_one;thing_two", values_row)

    def test_encrypted(self):
        CrfEncrypted.objects.create(
            subject_visit=self.subject_visit, encrypted1="value of encrypted field"
        )
        queryset = CrfEncrypted.objects.all()
        model_exporter = ModelExporter(
            queryset=queryset,
            lookups={"subject_identifier": "subject_visit__subject_identifier"},
        )
        path = model_exporter.export()
        with path.open() as f:
            csv_reader = csv.reader(f)
            rows = [row for row in enumerate(csv_reader)]
        values_row = rows[1][1][0]
        self.assertIn("<encrypted>", values_row)

    def test_encrypted_not_masked(self):
        CrfEncrypted.objects.create(
            subject_visit=self.subject_visit, encrypted1="value of encrypted field"
        )
        queryset = CrfEncrypted.objects.all()
        model_exporter = ModelExporter(
            queryset=queryset,
            encrypt=False,
            lookups={"subject_identifier": "subject_visit__subject_identifier"},
        )
        path = model_exporter.export()
        with path.open() as f:
            csv_reader = csv.reader(f)
            rows = [row for row in enumerate(csv_reader)]
        values_row = rows[1][1][0]
        self.assertIn("value of encrypted field", values_row)

    def test_export_history(self):
        self.crf.m2m.add(self.thing_one)
        self.crf.m2m.add(self.thing_two)
        queryset = Crf.objects.all()
        model_exporter = ModelExporter(
            queryset=queryset,
            lookups={"subject_identifier": "subject_visit__subject_identifier"},
        )
        path = model_exporter.export()
        obj = FileHistory.objects.get(filename=path.name)
        self.assertTrue(obj.exported)
        self.assertTrue(obj.exported_datetime)
        self.assertFalse(obj.sent)
        self.assertFalse(obj.sent_datetime)
        self.assertFalse(obj.received)
        self.assertFalse(obj.received_datetime)
        self.assertIn(str(self.crf.pk), obj.pk_list)

    def test_export_transaction(self):
        self.crf.m2m.add(self.thing_one)
        self.crf.m2m.add(self.thing_two)
        queryset = Crf.objects.all()
        model_exporter = ModelExporter(
            queryset=queryset,
            lookups={"subject_identifier": "subject_visit__subject_identifier"},
        )
        path = model_exporter.export()
        file_history_obj = FileHistory.objects.get(filename=path.name)
        tx_obj = ObjectHistory.objects.get(tx_pk=self.crf.pk)
        self.assertIn(str(tx_obj.export_uuid), file_history_obj.export_uuid_list)
        self.assertEqual(tx_obj.status, EXPORTED)

    def test_export_change_type_insert(self):
        self.crf.m2m.add(self.thing_one)
        self.crf.m2m.add(self.thing_two)
        queryset = Crf.objects.all()
        model_exporter = ModelExporter(
            queryset=queryset,
            lookups={"subject_identifier": "subject_visit__subject_identifier"},
        )
        model_exporter.export()
        model_exporter = ModelExporter(queryset=queryset)
        model_exporter.export()
        tx_qs = ObjectHistory.objects.filter(tx_pk=self.crf.pk).order_by("exported_datetime")
        self.assertEqual(tx_qs[0].export_change_type, INSERT)

    @skip("check insert/update flags?")
    def test_export_change_type_update(self):
        ObjectHistory.objects.all().delete()
        self.crf.m2m.add(self.thing_one)
        self.crf.m2m.add(self.thing_two)
        self.crf.appt_date = timezone.now()
        self.crf.save()
        queryset = Crf.objects.all()
        model_exporter = ModelExporter(
            queryset=queryset,
            lookups={"subject_identifier": "subject_visit__subject_identifier"},
        )
        model_exporter.export()
        sleep(1)
        model_exporter = ModelExporter(queryset=queryset)
        model_exporter.export()
        tx_qs = ObjectHistory.objects.filter(tx_pk=self.crf.pk).order_by("exported_datetime")
        self.assertEqual(tx_qs[0].export_change_type, INSERT)
        self.assertEqual(tx_qs[1].export_change_type, UPDATE)

    def test_export_change_type_in_csv(self):
        self.crf.m2m.add(self.thing_one)
        self.crf.m2m.add(self.thing_two)
        queryset = Crf.objects.all()
        model_exporter = ModelExporter(
            queryset=queryset,
            lookups={"subject_identifier": "subject_visit__subject_identifier"},
        )
        path = model_exporter.export()
        with path.open("r") as f:
            csv_reader = csv.DictReader(f, delimiter="|")
            rows = [row for row in enumerate(csv_reader)]
        values_row = rows[0][1]
        self.assertEqual(INSERT, values_row.get("export_change_type"))

    def test_export_change_type_in_csv_update(self):
        self.crf.m2m.add(self.thing_one)
        self.crf.m2m.add(self.thing_two)
        self.crf.appt_date = timezone.now()
        self.crf.save()
        queryset = CrfThree.objects.all()
        model_exporter = ModelExporter(
            queryset=queryset,
            lookups={"subject_identifier": "subject_visit__subject_identifier"},
        )
        path = model_exporter.export()
        with path.open() as f:
            csv_reader = csv.DictReader(f, delimiter="|")
            rows = [row for row in enumerate(csv_reader)]
        values_row = rows[0][1]
        self.assertEqual(INSERT, values_row.get("export_change_type"))
        values_row = rows[1][1]
        self.assertEqual(UPDATE, values_row.get("export_change_type"))

    def test_manager_creates_exported_tx(self):
        try:
            tx_obj = ObjectHistory.objects.get(tx_pk=self.crf.pk)
        except ObjectDoesNotExist:
            self.fail("ExportedTransaction unexpectedly does not exist.")
        self.assertEqual(tx_obj.export_change_type, INSERT)
