from clinicedc_constants import (
    FEMALE,
    GRADE3,
    GRAMS_PER_DECILITER,
    NO,
    NOT_APPLICABLE,
    PERCENT,
    TEN_X_9_PER_LITER,
    YES,
)
from clinicedc_tests.consents import consent_v1
from clinicedc_tests.helper import Helper
from clinicedc_tests.models import BloodResultsFbc
from clinicedc_tests.visit_schedules.visit_schedule import get_visit_schedule
from django.apps import apps as django_apps
from django.test import TestCase, override_settings, tag

from edc_consent import site_consents
from edc_lab.models import Panel
from edc_lab_results.get_summary import get_summary
from edc_visit_schedule.site_visit_schedules import site_visit_schedules


@tag("lab_results")
@override_settings(SITE_ID=10)
class TestBloodResult(TestCase):
    def setUp(self):
        site_consents.registry = {}
        site_consents.register(consent_v1)

        visit_schedule = get_visit_schedule(consent_v1)
        site_visit_schedules._registry = {}
        site_visit_schedules.register(visit_schedule)

        helper = Helper()
        subject_visit = helper.enroll_to_baseline(
            visit_schedule_name="visit_schedule", schedule_name="schedule", gender=FEMALE
        )
        self.subject_identifier = subject_visit.subject_identifier

        panel = Panel.objects.get(name="fbc")
        requisition = django_apps.get_model(
            "clinicedc_tests.subjectrequisition"
        ).objects.create(
            subject_visit=subject_visit,
            panel=panel,
            requisition_datetime=subject_visit.report_datetime,
        )
        self.data = dict(subject_visit=subject_visit, requisition=requisition)

    def test_ok(self):
        BloodResultsFbc.objects.create(**self.data)

    def test_summary_none(self):
        obj = BloodResultsFbc.objects.create(**self.data)
        reportable, abnormal, errors = get_summary(obj)
        self.assertEqual([], reportable)
        self.assertEqual([], abnormal)
        self.assertEqual([], errors)

    def test_summary_normal(self):
        self.data.update(
            haemoglobin_value=14,
            haemoglobin_units=GRAMS_PER_DECILITER,
            haemoglobin_abnormal=NO,
            haemoglobin_reportable=NOT_APPLICABLE,
            results_abnormal=NO,
            results_reportable=NOT_APPLICABLE,
        )
        obj = BloodResultsFbc.objects.create(**self.data)
        reportable, abnormal, errors = get_summary(obj)
        self.assertEqual([], reportable)
        self.assertEqual([], abnormal)
        self.assertEqual([], errors)

    def test_summary_abnormal(self):
        self.data.update(
            haemoglobin_value=12,
            haemoglobin_units=GRAMS_PER_DECILITER,
            haemoglobin_abnormal=YES,
            haemoglobin_reportable=GRADE3,
            results_abnormal=YES,
            results_reportable=NO,
        )
        obj = BloodResultsFbc.objects.create(**self.data)
        reportable, abnormal, errors = get_summary(obj)
        self.assertEqual([], reportable)
        self.assertEqual([], errors)
        abnormal_summary = "\n".join(abnormal)
        # female / 12 is still ok
        self.assertEqual("", abnormal_summary)
        obj.delete()

        self.data.update(
            haemoglobin_value=11,
            haemoglobin_units=GRAMS_PER_DECILITER,
            haemoglobin_abnormal=YES,
            haemoglobin_reportable=GRADE3,
            results_abnormal=YES,
            results_reportable=NO,
        )
        obj = BloodResultsFbc.objects.create(**self.data)
        reportable, abnormal, errors = get_summary(obj)
        self.assertEqual([], reportable)
        self.assertEqual([], errors)
        abnormal_summary = "\n".join(abnormal)
        self.assertIn("haemoglobin: 11 g/dL", abnormal_summary)

    def test_summary_g3(self):
        self.data.update(
            haemoglobin_value=7.5,
            haemoglobin_units=GRAMS_PER_DECILITER,
            haemoglobin_abnormal=YES,
            haemoglobin_reportable=GRADE3,
            results_abnormal=YES,
            results_reportable=YES,
        )
        obj = BloodResultsFbc.objects.create(**self.data)
        reportable, abnormal, errors = get_summary(obj)
        self.assertIn("haemoglobin: 6.5<=7.5<8.5 g/dL GRADE3", "\n".join(reportable))
        self.assertEqual([], abnormal)
        self.assertEqual([], errors)

    def test_missing(self):
        obj = BloodResultsFbc.objects.create(**self.data)
        self.assertEqual(obj.missing_count, 5)
        self.assertEqual(
            "haemoglobin_value,hct_value,rbc_value,wbc_value,platelets_value",
            obj.missing,
        )

        obj.haemoglobin_value = 14
        obj.haemoglobin_units = GRAMS_PER_DECILITER
        obj.save()
        self.assertEqual(obj.missing_count, 4)
        self.assertEqual("hct_value,rbc_value,wbc_value,platelets_value", obj.missing)

        obj.hct_value = 10
        obj.hct_units = PERCENT
        obj.save()
        self.assertEqual(obj.missing_count, 3)
        self.assertEqual("rbc_value,wbc_value,platelets_value", obj.missing)

        obj.rbc_value = 10
        obj.rbc_units = TEN_X_9_PER_LITER
        obj.save()
        self.assertEqual(obj.missing_count, 2)
        self.assertEqual("wbc_value,platelets_value", obj.missing)

        obj.wbc_value = 10
        obj.wbc_units = TEN_X_9_PER_LITER
        obj.save()
        self.assertEqual(obj.missing_count, 1)
        self.assertEqual("platelets_value", obj.missing)

        obj.platelets_value = 10
        obj.platelets_units = TEN_X_9_PER_LITER
        obj.save()
        self.assertEqual(obj.missing_count, 0)
        self.assertEqual("", obj.missing)

        obj.platelets_value = None
        obj.platelets_units = None
        obj.save()
        self.assertEqual(obj.missing_count, 1)
        self.assertEqual("platelets_value", obj.missing)
