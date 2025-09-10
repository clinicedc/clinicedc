from copy import deepcopy

from django.conf import settings
from django.contrib.sites.models import Site
from django.test import TestCase

from edc_action_item.site_action_items import site_action_items
from edc_consent import site_consents
from edc_constants.constants import GRADE3, GRADE4, NO, NOT_APPLICABLE, YES
from edc_lab import site_labs
from edc_lab.models import Panel
from edc_lab_results.action_items import register_actions
from edc_reportable import GRAMS_PER_DECILITER, PERCENT
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from tests.consents import consent_v1
from tests.helper import Helper
from tests.models import SubjectRequisition
from tests.visit_schedules.visit_schedule_lab_results.lab_profiles import lab_profile
from tests.visit_schedules.visit_schedule_lab_results.visit_schedule import (
    get_visit_schedule,
)

from ..forms import BloodResultsFbcForm, BloodResultsHba1cForm


class TestBloodResultForm(TestCase):
    def setUp(self):
        helper = Helper()
        site_labs.register(lab_profile=lab_profile)

        site_action_items.registry = {}
        register_actions()
        site_consents.registry = {}
        site_consents.register(consent_v1)
        site_visit_schedules._registry = {}
        site_visit_schedules.loaded = False
        site_visit_schedules.register(get_visit_schedule(consent_v1))

        self.subject_visit = helper.enroll_to_baseline(consent_definition=consent_v1)
        self.subject_identifier = self.subject_visit.subject_identifier

        fbc_panel = Panel.objects.get(name="fbc")
        requisition = SubjectRequisition.objects.create(
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
            site=Site.objects.get(id=settings.SITE_ID),
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

    def test_haemoglobin_g3_male(self):
        data = deepcopy(self.data)
        data.update(
            haemoglobin_value=7.1,
            haemoglobin_units=GRAMS_PER_DECILITER,
            haemoglobin_abnormal=YES,
            haemoglobin_reportable=GRADE3,
            results_abnormal=YES,
            results_reportable=YES,
        )
        form = BloodResultsFbcForm(data=data)
        form.is_valid()
        self.assertEqual({}, form._errors)

    def test_haemoglobin_g4_male(self):
        data = deepcopy(self.data)
        data.update(
            haemoglobin_value=5.0,
            haemoglobin_units=GRAMS_PER_DECILITER,
            haemoglobin_abnormal=YES,
            haemoglobin_reportable=GRADE4,
            results_abnormal=YES,
            results_reportable=YES,
        )
        form = BloodResultsFbcForm(data=data)
        form.is_valid()
        self.assertEqual({}, form._errors)


class TestBloodResultFormForPoc(TestCase):
    def setUp(self):
        helper = Helper()
        site_action_items.registry = {}
        register_actions()
        site_consents.registry = {}
        site_consents.register(consent_v1)
        site_visit_schedules._registry = {}
        site_visit_schedules.loaded = False
        site_visit_schedules.register(get_visit_schedule(consent_v1))

        self.subject_visit = helper.enroll_to_baseline(consent_definition=consent_v1)
        self.subject_identifier = self.subject_visit.subject_identifier

        self.data = dict(
            report_datetime=self.subject_visit.report_datetime,
            subject_visit=self.subject_visit,
            assay_datetime=self.subject_visit.report_datetime,
            results_reportable=NOT_APPLICABLE,
            results_abnormal=NO,
            site=Site.objects.get(id=settings.SITE_ID),
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
        requisition = SubjectRequisition.objects.create(
            subject_visit=self.subject_visit,
            panel=hba1c_panel,
            requisition_datetime=self.subject_visit.report_datetime,
        )

        data.update(requisition=requisition, hba1c_value=5.0)
        form = BloodResultsHba1cForm(data=data)
        form.is_valid()
        self.assertIn(
            "This field is not required", str(form._errors.get("subject_requisition"))
        )

    def test_not_poc_requires_requisition(self):
        data = deepcopy(self.data)

        data.update(is_poc=NO)
        form = BloodResultsHba1cForm(data=data)
        form.is_valid()
        self.assertIn(
            "This field is required", str(form._errors.get("subject_requisition"))
        )

        hba1c_panel = Panel.objects.get(name="hba1c")
        requisition = SubjectRequisition.objects.create(
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
