from django.apps import apps as django_apps
from django.test import TestCase
from edc_appointment.models import Appointment
from edc_constants.constants import NO, NOT_APPLICABLE, YES
from edc_lab.models import Panel
from edc_reportable import GRADE3, GRAMS_PER_DECILITER, PERCENT, TEN_X_9_PER_LITER
from edc_utils import get_utcnow
from edc_visit_tracking.constants import SCHEDULED

from ..models import BloodResultsFbc
from ..test_case_mixin import TestCaseMixin


class TestBloodResult(TestCaseMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.subject_identifier = self.enroll()
        appointment = Appointment.objects.get(
            subject_identifier=self.subject_identifier,
            visit_code="1000",
        )
        subject_visit = django_apps.get_model(
            "edc_visit_tracking.subjectvisit"
        ).objects.create(
            report_datetime=get_utcnow(),
            appointment=appointment,
            reason=SCHEDULED,
        )
        panel = Panel.objects.get(name="fbc")
        requisition = django_apps.get_model("edc_metadata.subjectrequisition").objects.create(
            subject_visit=subject_visit,
            panel=panel,
            requisition_datetime=subject_visit.report_datetime,
        )
        self.data = dict(subject_visit=subject_visit, requisition=requisition)

    def test_ok(self):
        BloodResultsFbc.objects.create(**self.data)

    def test_summary_none(self):
        obj = BloodResultsFbc.objects.create(**self.data)
        self.assertEqual(obj.get_summary(), [])

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
        summary = obj.get_summary()
        self.assertEqual([], summary)

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
        summary = obj.get_summary()
        self.assertIn("haemoglobin_value: 12 g/dL is abnormal", summary)

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
        summary = obj.get_summary()
        self.assertIn("haemoglobin_value: 7.0<=7.5<9.0 g/dL GRADE 3.", summary)

    def test_missing(self):
        obj = BloodResultsFbc.objects.create(**self.data)
        self.assertEqual(obj.missing_count, 5)
        self.assertEqual(
            "haemoglobin_value,hct_value,rbc_value,wbc_value,platelets_value", obj.missing
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
        self.assertEqual(None, obj.missing)

        obj.platelets_value = None
        obj.platelets_units = None
        obj.save()
        self.assertEqual(obj.missing_count, 1)
        self.assertEqual("platelets_value", obj.missing)
