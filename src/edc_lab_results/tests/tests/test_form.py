from copy import deepcopy

from django.apps import apps as django_apps
from django.test import TestCase
from edc_action_item import site_action_items
from edc_appointment.models import Appointment
from edc_constants.constants import NO, NOT_APPLICABLE, YES
from edc_lab.models import Panel
from edc_reportable import GRADE3, GRAMS_PER_DECILITER, PERCENT
from edc_utils import get_utcnow
from edc_visit_tracking.constants import SCHEDULED

from edc_lab_results.action_items import register_actions

from ..forms import BloodResultsFbcForm, BloodResultsHba1cForm
from ..test_case_mixin import TestCaseMixin


class TestBloodResultForm(TestCaseMixin, TestCase):
    def setUp(self):
        site_action_items.registry = {}
        register_actions()
        self.subject_identifier = self.enroll()
        appointment = Appointment.objects.get(
            subject_identifier=self.subject_identifier,
            visit_code="1000",
        )
        self.subject_visit = django_apps.get_model(
            "edc_visit_tracking.subjectvisit"
        ).objects.create(
            report_datetime=get_utcnow(),
            appointment=appointment,
            reason=SCHEDULED,
        )
        fbc_panel = Panel.objects.get(name="fbc")
        requisition = django_apps.get_model("edc_metadata.subjectrequisition").objects.create(
            subject_visit=self.subject_visit,
            panel=fbc_panel,
            requisition_datetime=self.subject_visit.report_datetime,
        )
        self.data = dict(
            report_datetime=self.subject_visit.report_datetime,
            subject_visit=self.subject_visit,
            assay_datetime=self.subject_visit.report_datetime,
            requisition=requisition,
            action_identifier="-",
            results_reportable=NOT_APPLICABLE,
            results_abnormal=NO,
        )

    def test_fbc_ok(self):
        data = deepcopy(self.data)
        form = BloodResultsFbcForm(data=data)
        form.is_valid()
        self.assertEqual({}, form._errors)

    def test_missing_units(self):
        data = deepcopy(self.data)
        data.update(haemoglobin_value=10)
        form = BloodResultsFbcForm(data=data)
        form.is_valid()
        self.assertIn("haemoglobin_units", form._errors)

    def test_haemoglobin_abnormal_required(self):
        data = deepcopy(self.data)
        data.update(haemoglobin_value=10, haemoglobin_units=GRAMS_PER_DECILITER)
        form = BloodResultsFbcForm(data=data)
        form.is_valid()
        self.assertIn("haemoglobin_abnormal", form._errors)

    def test_haemoglobin_reportable_required(self):
        data = deepcopy(self.data)
        data.update(
            haemoglobin_value=10,
            haemoglobin_units=GRAMS_PER_DECILITER,
            haemoglobin_abnormal=NO,
        )
        form = BloodResultsFbcForm(data=data)
        form.is_valid()
        self.assertIn("haemoglobin_reportable", form._errors)

    def test_haemoglobin_normal(self):
        data = deepcopy(self.data)
        data.update(
            haemoglobin_value=14,
            haemoglobin_units=GRAMS_PER_DECILITER,
            haemoglobin_abnormal=NO,
            haemoglobin_reportable=NOT_APPLICABLE,
        )
        form = BloodResultsFbcForm(data=data)
        form.is_valid()
        self.assertEqual({}, form._errors)

    def test_haemoglobin_high(self):
        data = deepcopy(self.data)
        data.update(
            haemoglobin_value=18,
            haemoglobin_units=GRAMS_PER_DECILITER,
            haemoglobin_abnormal=YES,
            haemoglobin_reportable=NO,
            results_abnormal=YES,
            results_reportable=NO,
        )
        form = BloodResultsFbcForm(data=data)
        form.is_valid()
        self.assertEqual({}, form._errors)

    def test_haemoglobin_g4(self):
        data = deepcopy(self.data)
        data.update(
            haemoglobin_value=7.5,
            haemoglobin_units=GRAMS_PER_DECILITER,
            haemoglobin_abnormal=YES,
            haemoglobin_reportable=GRADE3,
            results_abnormal=YES,
            results_reportable=YES,
        )
        form = BloodResultsFbcForm(data=data)
        form.is_valid()
        self.assertEqual({}, form._errors)


class TestBloodResultFormForPoc(TestCaseMixin, TestCase):
    def setUp(self):
        super().setUp()
        site_action_items.registry = {}
        register_actions()
        self.subject_identifier = self.enroll()
        appointment = Appointment.objects.get(
            subject_identifier=self.subject_identifier,
            visit_code="1000",
        )
        self.subject_visit = django_apps.get_model(
            "edc_visit_tracking.subjectvisit"
        ).objects.create(
            report_datetime=get_utcnow(),
            appointment=appointment,
            reason=SCHEDULED,
        )
        self.data = dict(
            report_datetime=self.subject_visit.report_datetime,
            subject_visit=self.subject_visit,
            assay_datetime=self.subject_visit.report_datetime,
            results_reportable=NOT_APPLICABLE,
            results_abnormal=NO,
        )

    def test_is_poc_does_not_require_requisition(self):
        data = deepcopy(self.data)

        data.update(is_poc=YES)
        form = BloodResultsHba1cForm(data=data)
        form.is_valid()
        self.assertEqual({}, form._errors)

        data.update(
            hba1c_value=5.0,
            hba1c_units=PERCENT,
            hba1c_abnormal=NO,
            hba1c_reportable=NOT_APPLICABLE,
        )
        form = BloodResultsHba1cForm(data=data)
        form.is_valid()
        self.assertEqual({}, form._errors)

        data.update(hba1c_value=4.3)
        form = BloodResultsHba1cForm(data=data)
        form.is_valid()
        self.assertIn("HBA1C is abnormal", str(form._errors.get("hba1c_value")))

        hba1c_panel = Panel.objects.get(name="hba1c")
        requisition = django_apps.get_model("edc_metadata.subjectrequisition").objects.create(
            subject_visit=self.subject_visit,
            panel=hba1c_panel,
            requisition_datetime=self.subject_visit.report_datetime,
        )

        data.update(requisition=requisition, hba1c_value=5.0)
        form = BloodResultsHba1cForm(data=data)
        form.is_valid()
        self.assertIn("This field is not required", str(form._errors.get("requisition")))

    def test_not_poc_requires_requisition(self):
        data = deepcopy(self.data)

        data.update(is_poc=NO)
        form = BloodResultsHba1cForm(data=data)
        form.is_valid()
        self.assertIn("This field is required", str(form._errors.get("requisition")))

        hba1c_panel = Panel.objects.get(name="hba1c")
        requisition = django_apps.get_model("edc_metadata.subjectrequisition").objects.create(
            subject_visit=self.subject_visit,
            panel=hba1c_panel,
            requisition_datetime=self.subject_visit.report_datetime,
        )

        data.update(requisition=requisition)
        form = BloodResultsHba1cForm(data=data)
        form.is_valid()
        self.assertEqual({}, form._errors)

        data.update(
            hba1c_value=5.0,
            hba1c_units=PERCENT,
            hba1c_abnormal=NO,
            hba1c_reportable=NOT_APPLICABLE,
        )
        form = BloodResultsHba1cForm(data=data)
        form.is_valid()
        self.assertEqual({}, form._errors)
