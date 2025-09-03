import csv
from tempfile import mkdtemp

from django.test import TestCase, override_settings

from edc_consent import site_consents
from edc_facility.import_holidays import import_holidays
from edc_pdutils.df_exporters import TablesExporter
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from tests.consents import consent_v1
from tests.helper import Helper
from tests.visit_schedules.visit_schedule_pdutils.visit_schedule import (
    get_visit_schedule,
)


@override_settings(EDC_EXPORT_EXPORT_FOLDER=mkdtemp())
class TestExport(TestCase):
    helper = Helper()

    @classmethod
    def setUpTestData(cls):
        import_holidays()

    def setUp(self):
        helper = Helper()
        site_consents.registry = {}
        site_consents.register(consent_v1)

        site_visit_schedules._registry = {}
        site_visit_schedules.register(get_visit_schedule(consent_v1, 5))

        for i in range(0, 5):
            helper.consent_and_put_on_schedule(
                visit_schedule_name="visit_schedule", schedule_name="schedule"
            )
            self.helper.create_crfs()

    def test_tables_to_csv_lower_columns(self):
        tables_exporter = TablesExporter(app_label="edc_pdutils")
        for path in tables_exporter.exported_paths.values():
            with open(path, "r") as f:
                csv_reader = csv.DictReader(f, delimiter="|")
                for row in csv_reader:
                    for field in row:
                        self.assertEqual(field.lower(), field)
                    break

    def test_tables_to_csv_from_app_label(self):
        tables_exporter = TablesExporter(app_label="edc_pdutils")
        for path in tables_exporter.exported_paths.values():
            with open(path, "r") as f:
                csv_reader = csv.DictReader(f, delimiter="|")
                rows = [row for row in enumerate(csv_reader)]
            self.assertGreater(len(rows), 0)

    def test_tables_to_csv_from_app_label_exclude_history(self):
        class MyTablesExporter(TablesExporter):
            exclude_history_tables = True

        tables_exporter = MyTablesExporter(app_label="edc_pdutils")
        for path in tables_exporter.exported_paths:
            self.assertNotIn("history", path)
