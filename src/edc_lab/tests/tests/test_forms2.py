from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import time_machine
from clinicedc_tests.consents import consent_v1
from clinicedc_tests.helper import Helper
from clinicedc_tests.labs import lab_profile
from clinicedc_tests.models import SubjectRequisition
from clinicedc_tests.sites import all_sites
from clinicedc_tests.visit_schedules.visit_schedule import get_visit_schedule
from django import forms
from django.core.exceptions import NON_FIELD_ERRORS
from django.test import TestCase, override_settings, tag
from django.utils import timezone

from edc_appointment.models import Appointment
from edc_constants.constants import YES
from edc_crf.modelform_mixins import RequisitionModelFormMixin
from edc_facility.import_holidays import import_holidays
from edc_lab import site_labs
from edc_lab.form_validators import (
    RequisitionFormValidator as BaseRequisitionFormValidator,
)
from edc_lab.models import Aliquot
from edc_lab_panel.panels import vl_panel
from edc_sites.site import sites as site_sites
from edc_sites.utils import add_or_update_django_sites
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED
from edc_visit_tracking.models import SubjectVisit

utc_tz = ZoneInfo("UTC")


class RequisitionFormValidator(BaseRequisitionFormValidator):
    def validate_demographics(self):
        pass


class RequisitionForm(RequisitionModelFormMixin, forms.ModelForm):
    form_validator_cls = RequisitionFormValidator

    def validate_against_consent(self):
        pass

    class Meta:
        fields = "__all__"
        model = SubjectRequisition


@tag("lab")
@override_settings(SITE_ID=10)
@time_machine.travel(datetime(2025, 6, 11, 8, 00, tzinfo=utc_tz))
class TestForms2(TestCase):
    @classmethod
    def setUpTestData(cls):
        import_holidays()
        site_sites._registry = {}
        site_sites.loaded = False
        site_sites.register(*all_sites)
        add_or_update_django_sites()

    def setUp(self):
        site_labs.initialize()
        site_labs.register(lab_profile=lab_profile)

        site_visit_schedules._registry = {}
        visit_schedule = get_visit_schedule(consent_v1)
        site_visit_schedules.register(visit_schedule)

        self.helper = Helper()
        subject_consent = self.helper.consent_and_put_on_schedule(
            visit_schedule_name="visit_schedule",
            schedule_name="schedule",
            age_in_years=25,
        )
        self.subject_identifier = subject_consent.subject_identifier
        appointment = Appointment.objects.get(visit_code="1000")
        self.subject_visit = SubjectVisit.objects.create(
            appointment=appointment, report_datetime=timezone.now(), reason=SCHEDULED
        )

    def test_requisition_form_packed_cannot_change(self):
        obj = SubjectRequisition.objects.create(
            subject_visit=self.subject_visit,
            panel=vl_panel.panel_model_obj,
            packed=True,
            processed=True,
            received=True,
        )
        data = {"packed": False, "processed": True, "received": True}
        form = RequisitionForm(data=data, instance=obj)
        form.is_valid()
        self.assertIn("packed", list(form.errors.keys()))

    def test_requisition_form_processed_can_change_if_no_aliquots(self):
        obj = SubjectRequisition.objects.create(
            subject_visit=self.subject_visit,
            panel=vl_panel.panel_model_obj,
            packed=True,
            processed=True,
            received=True,
        )
        data = {"packed": True, "processed": False, "received": True}
        form = RequisitionForm(data=data, instance=obj)
        form.is_valid()
        self.assertNotIn("processed", list(form.errors.keys()))

    def test_requisition_form_processed_cannot_change_if_aliquots(self):
        obj = SubjectRequisition.objects.create(
            subject_visit=self.subject_visit,
            panel=vl_panel.panel_model_obj,
            packed=True,
            processed=True,
            received=True,
        )
        Aliquot.objects.create(
            aliquot_identifier="1111",
            requisition_identifier=obj.requisition_identifier,
            count=1,
        )
        data = {"packed": True, "processed": False, "received": True}
        form = RequisitionForm(data=data, instance=obj)
        form.is_valid()
        self.assertIn("processed", list(form.errors.keys()))

    def test_requisition_form_received_cannot_change(self):
        obj = SubjectRequisition.objects.create(
            subject_visit=self.subject_visit,
            panel=vl_panel.panel_model_obj,
            packed=True,
            processed=True,
            received=True,
        )
        data = {"packed": True, "processed": True, "received": False}
        form = RequisitionForm(data=data, instance=obj)
        form.is_valid()
        self.assertIn("received", list(form.errors.keys()))

    def test_requisition_form_received_cannot_be_set_by_form(self):
        obj = SubjectRequisition.objects.create(
            subject_visit=self.subject_visit,
            panel=vl_panel.panel_model_obj,
            received=False,
        )
        data = {"received": True}
        form = RequisitionForm(data=data, instance=obj)
        form.is_valid()
        self.assertIn("received", list(form.errors.keys()))

    def test_requisition_form_cannot_be_changed_if_received(self):
        obj = SubjectRequisition.objects.create(
            report_datetime=self.subject_visit.report_datetime,
            subject_visit=self.subject_visit,
            panel=vl_panel.panel_model_obj,
            received=True,
        )
        data = {"received": True}
        form = RequisitionForm(data=data, instance=obj)
        form.is_valid()
        self.assertIn(
            "Requisition may not be changed", "".join(form.errors.get(NON_FIELD_ERRORS))
        )

    def test_requisition_form_dates(self):
        class MyRequisitionFormValidator(BaseRequisitionFormValidator):
            def validate_demographics(self):
                pass

        class MyRequisitionForm(RequisitionModelFormMixin, forms.ModelForm):
            form_validator_cls = MyRequisitionFormValidator

            class Meta:
                fields = "__all__"
                model = SubjectRequisition

        data = {
            "is_drawn": YES,
            "drawn_datetime": self.subject_visit.report_datetime,
            "requisition_datetime": self.subject_visit.report_datetime - timedelta(days=3),
            "subject_visit": self.subject_visit.pk,
            "report_datetime": self.subject_visit.report_datetime - timedelta(days=3),
            "subject_identifier": self.subject_visit.subject_identifier,
            "panel": vl_panel.panel_model_obj,
        }
        form = MyRequisitionForm(data=data, instance=SubjectRequisition())
        form.is_valid()
        self.assertIn("requisition_datetime", form._errors)
        self.assertIn(
            "Invalid. Date falls outside of the window period",
            form.errors.get("requisition_datetime")[0],
        )
