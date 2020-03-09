import csv
import os
import uuid

from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase, tag
from edc_utils import get_utcnow
from edc_pdutils.model_to_dataframe import ValueGetterInvalidLookup
from time import sleep
from unittest.case import skip

from ..constants import EXPORTED, UPDATE, INSERT
from ..model_exporter import ModelExporter
from ..models import ObjectHistory, FileHistory
from .models import Crf, SubjectVisit, ListModel, CrfEncrypted

app_config = django_apps.get_app_config("edc_export")


class TestExportModel(TestCase):

    path = app_config.export_folder

    def setUp(self):
        self.thing_one = ListModel.objects.create(
            display_name="thing_one", name="thing_one"
        )
        self.thing_two = ListModel.objects.create(
            display_name="thing_two", name="thing_two"
        )
        self.subject_visit = SubjectVisit.objects.create(
            subject_identifier="12345", report_datetime=get_utcnow()
        )
        self.crf = Crf.objects.create(
            subject_visit=self.subject_visit,
            char1="char",
            date1=get_utcnow(),
            int1=1,
            uuid1=uuid.uuid4(),
        )

    def tearDown(self):
        """Remove .csv files created in tests.
        """
        super().tearDown()
        if "edc_export" not in self.path:
            raise ValueError(f"Invalid path in test. Got {self.path}")
        files = os.listdir(self.path)
        for file in files:
            if ".csv" in file:
                file = os.path.join(self.path, file)
                os.remove(file)

    def test_model(self):
        ModelExporter(
            model="edc_export.crf",
            lookups={"subject_identifier": "subject_visit__subject_identifier"},
        )

    def test_queryset_no_data(self):
        Crf.objects.all().delete()
        queryset = Crf.objects.all()
        self.assertEqual(queryset.model, Crf)
        ModelExporter(queryset=queryset)

    def test_export_file(self):
        """Assert creates file.
        """
        Crf.objects.all().delete()
        queryset = Crf.objects.all()
        self.assertEqual(queryset.model, Crf)
        model_exporter = ModelExporter(
            queryset=queryset,
            lookups={"subject_identifier": "subject_visit__subject_identifier"},
        )
        path = model_exporter.export()
        self.assertTrue(os.path.exists(path))
        self.assertIn("edc_export_crf_", path)

    def test_field_names(self):
        Crf.objects.all().delete()
        queryset = Crf.objects.all()
        self.assertEqual(queryset.model, Crf)
        model_exporter = ModelExporter(
            queryset=queryset,
            lookups={"subject_identifier": "subject_visit__subject_identifier"},
        )
        self.assertIn("char1", model_exporter.field_names)
        self.assertIn("date1", model_exporter.field_names)
        self.assertIn("int1", model_exporter.field_names)
        self.assertIn("uuid1", model_exporter.field_names)
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
            exclude_field_names=["date1", "uuid1"],
            lookups={"subject_identifier": "subject_visit__subject_identifier"},
        )
        self.assertIn("char1", model_exporter.field_names)
        self.assertNotIn("date1", model_exporter.field_names)
        self.assertIn("int1", model_exporter.field_names)
        self.assertNotIn("uuid1", model_exporter.field_names)
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
            field_names=["char1"],
            lookups={"subject_identifier": "subject_visit__subject_identifier"},
        )
        self.assertIn("char1", model_exporter.field_names)
        self.assertNotIn("date1", model_exporter.field_names)
        self.assertNotIn("int1", model_exporter.field_names)
        self.assertNotIn("uuid1", model_exporter.field_names)
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
        with open(path, "r") as f:
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
        with open(path, "r") as f:
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
        with open(path, "r") as f:
            csv_reader = csv.reader(f)
            rows = [row for row in enumerate(csv_reader)]
        values_row = rows[1][1][0]
        self.assertEqual(len(values_row.split("|")), 28)

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
        with open(path, "r") as f:
            csv_reader = csv.reader(f)
            rows = [row for row in enumerate(csv_reader)]
        values_row = rows[1][1][0]
        self.assertIn("thing_one;thing_two", values_row)

    def test_encrypted(self):
        subject_visit = SubjectVisit.objects.create(
            subject_identifier="12345", report_datetime=get_utcnow()
        )
        CrfEncrypted.objects.create(
            subject_visit=subject_visit, encrypted1="value of encrypted field"
        )
        queryset = CrfEncrypted.objects.all()
        model_exporter = ModelExporter(
            queryset=queryset,
            lookups={"subject_identifier": "subject_visit__subject_identifier"},
        )
        path = model_exporter.export()
        with open(path, "r") as f:
            csv_reader = csv.reader(f)
            rows = [row for row in enumerate(csv_reader)]
        values_row = rows[1][1][0]
        self.assertIn("<encrypted>", values_row)

    def test_encrypted_not_masked(self):
        subject_visit = SubjectVisit.objects.create(
            subject_identifier="12345", report_datetime=get_utcnow()
        )
        CrfEncrypted.objects.create(
            subject_visit=subject_visit, encrypted1="value of encrypted field"
        )
        queryset = CrfEncrypted.objects.all()
        model_exporter = ModelExporter(
            queryset=queryset,
            encrypt=False,
            lookups={"subject_identifier": "subject_visit__subject_identifier"},
        )
        path = model_exporter.export()
        with open(path, "r") as f:
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
        obj = FileHistory.objects.get(filename=os.path.basename(path))
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
        file_history_obj = FileHistory.objects.get(filename=os.path.basename(path))
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
        tx_qs = ObjectHistory.objects.filter(tx_pk=self.crf.pk).order_by(
            "exported_datetime"
        )
        self.assertEqual(tx_qs[0].export_change_type, INSERT)

    @skip("check insert/update flags?")
    def test_export_change_type_update(self):
        ObjectHistory.objects.all().delete()
        self.crf.m2m.add(self.thing_one)
        self.crf.m2m.add(self.thing_two)
        self.crf.date1 = get_utcnow()
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
        tx_qs = ObjectHistory.objects.filter(tx_pk=self.crf.pk).order_by(
            "exported_datetime"
        )
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
        with open(path, "r") as f:
            csv_reader = csv.DictReader(f, delimiter="|")
            rows = [row for row in enumerate(csv_reader)]
        values_row = rows[0][1]
        self.assertEqual(INSERT, values_row.get("export_change_type"))

    def test_export_change_type_in_csv_update(self):
        self.crf.m2m.add(self.thing_one)
        self.crf.m2m.add(self.thing_two)
        self.crf.date1 = get_utcnow()
        self.crf.save()
        queryset = Crf.objects.all()
        model_exporter = ModelExporter(
            queryset=queryset,
            lookups={"subject_identifier": "subject_visit__subject_identifier"},
        )
        path = model_exporter.export()
        with open(path, "r") as f:
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
