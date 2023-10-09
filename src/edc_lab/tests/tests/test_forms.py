from datetime import timedelta

from django import forms
from django.conf import settings
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError
from django.test import TestCase
from edc_appointment.models import Appointment
from edc_appointment.tests.helper import Helper
from edc_constants.constants import NO, NOT_APPLICABLE, OTHER, YES
from edc_crf.modelform_mixins import RequisitionModelFormMixin
from edc_facility.import_holidays import import_holidays
from edc_form_validators import FormValidator
from edc_sites import add_or_update_django_sites
from edc_sites.single_site import SingleSite
from edc_utils import get_utcnow
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED

from edc_lab.form_validators import (
    RequisitionFormValidator as BaseRequisitionFormValidator,
)
from edc_lab.form_validators.requisition_form_validator import (
    RequisitionFormValidatorMixin,
)
from edc_lab.forms import BoxForm, BoxTypeForm, ManifestForm
from edc_lab.models import Aliquot
from lab_app.models import SubjectRequisition, SubjectVisit

from ..site_labs_test_helper import SiteLabsTestHelper
from ..visit_schedules import visit_schedule


class TestForms(TestCase):
    @classmethod
    def setUpClass(cls):
        add_or_update_django_sites(
            sites=[
                SingleSite(
                    settings.SITE_ID,
                    "test_site",
                    country_code="ug",
                    country="uganda",
                    domain="bugamba.ug.clinicedc.org",
                )
            ]
        )
        return super().setUpClass()

    def setUp(self):
        site_visit_schedules._registry = {}
        site_visit_schedules.register(visit_schedule)

    def test_box_form_specimen_types1(self):
        data = {"specimen_types": "12, 13"}
        form = BoxForm(data=data)
        form.is_valid()
        self.assertNotIn("specimen_types", list(form.errors.keys()))

    def test_box_form_specimen_types2(self):
        data = {"specimen_types": None}
        form = BoxForm(data=data)
        form.is_valid()
        self.assertIn("specimen_types", list(form.errors.keys()))

    def test_box_form_specimen_types3(self):
        data = {"specimen_types": "AA, BB"}
        form = BoxForm(data=data)
        form.is_valid()
        self.assertIn("specimen_types", list(form.errors.keys()))

    def test_box_form_specimen_types4(self):
        data = {"specimen_types": "12, 13, AA"}
        form = BoxForm(data=data)
        form.is_valid()
        self.assertIn("specimen_types", list(form.errors.keys()))

    def test_box_form_specimen_types5(self):
        data = {"specimen_types": "12, 13, 13"}
        form = BoxForm(data=data)
        form.is_valid()
        self.assertIn("specimen_types", list(form.errors.keys()))

    def test_box_type_form1(self):
        data = {"across": 5, "down": 6, "total": 30}
        form = BoxTypeForm(data=data)
        form.is_valid()
        self.assertNotIn("total", list(form.errors.keys()))

    def test_box_type_form2(self):
        data = {"across": 5, "down": 6, "total": 10}
        form = BoxTypeForm(data=data)
        form.is_valid()
        self.assertIn("total", list(form.errors.keys()))

    def test_manifest_form1(self):
        data = {"category": OTHER, "category_other": None}
        form = ManifestForm(data=data)
        form.is_valid()
        self.assertIn("category_other", list(form.errors.keys()))

    def test_manifest_form2(self):
        data = {"category": "blah", "category_other": None}
        form = ManifestForm(data=data)
        form.is_valid()
        self.assertNotIn("category_other", list(form.errors.keys()))

    def test_requisition_form_reason(self):
        class MyRequisitionFormValidator(RequisitionFormValidatorMixin, FormValidator):
            report_datetime_field_attr = "requisition_datetime"

            @property
            def report_datetime(self):
                return self.cleaned_data.get(self.report_datetime_field_attr)

        data = {"is_drawn": YES, "reason_not_drawn": NOT_APPLICABLE}
        form_validator = MyRequisitionFormValidator(
            cleaned_data=data, model=SubjectRequisition
        )
        with self.assertRaises(ValidationError) as cm:
            form_validator.validate()
        self.assertNotIn("reason_not_drawn", cm.exception.error_dict)

        data = {
            "is_drawn": NO,
            "reason_not_drawn": "collection_failed",
            "item_type": NOT_APPLICABLE,
        }
        form_validator = MyRequisitionFormValidator(
            cleaned_data=data, model=SubjectRequisition
        )
        try:
            form_validator.validate()
        except ValidationError:
            self.fail("ValidationError unexpectedly raised")

    def test_requisition_form_drawn_not_drawn(self):
        class MyRequisitionFormValidator(RequisitionFormValidatorMixin, FormValidator):
            report_datetime_field_attr = "requisition_datetime"

            @property
            def report_datetime(self):
                return self.cleaned_data.get(self.report_datetime_field_attr)

        data = {"is_drawn": YES, "drawn_datetime": None, "requisition_datetime": get_utcnow()}
        form_validator = MyRequisitionFormValidator(
            cleaned_data=data, model=SubjectRequisition
        )
        with self.assertRaises(ValidationError) as cm:
            form_validator.validate()
        self.assertIn("drawn_datetime", cm.exception.error_dict)

        self.assertEqual(
            cm.exception.error_dict.get("drawn_datetime")[0].message,
            "This field is required.",
        )

        data = {"is_drawn": NO, "drawn_datetime": get_utcnow()}
        form_validator = MyRequisitionFormValidator(
            cleaned_data=data, model=SubjectRequisition
        )
        with self.assertRaises(ValidationError) as cm:
            form_validator.validate()
        self.assertIn("drawn_datetime", cm.exception.error_dict)
        self.assertEqual(
            cm.exception.error_dict.get("drawn_datetime")[0].message,
            "This field is not required.",
        )

        data = {"is_drawn": NO, "drawn_datetime": None}
        form_validator = MyRequisitionFormValidator(
            cleaned_data=data, model=SubjectRequisition
        )
        try:
            form_validator.validate()
        except ValidationError:
            self.fail("ValidationError unexpectedly raised")


class TestForms2(TestCase):
    lab_helper = SiteLabsTestHelper()

    @classmethod
    def setUpClass(cls):
        add_or_update_django_sites(
            sites=[
                SingleSite(
                    settings.SITE_ID,
                    "test_site",
                    country_code="ug",
                    country="uganda",
                    domain="bugamba.ug.clinicedc.org",
                )
            ]
        )
        import_holidays()
        return super().setUpClass()

    def setUp(self):
        site_visit_schedules._registry = {}
        site_visit_schedules.register(visit_schedule)
        self.lab_helper.setup_site_labs()

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

        self.form_cls = RequisitionForm
        self.subject_identifier = "12345"
        self.lab_helper.setup_site_labs()
        self.panel = self.lab_helper.panel
        self.helper = Helper(subject_identifier=self.subject_identifier)
        self.helper.consent_and_put_on_schedule(
            visit_schedule_name="visit_schedule",
            schedule_name="schedule",
            age_in_years=25,
        )
        appointment = Appointment.objects.get(visit_code="1000")
        self.subject_visit = SubjectVisit.objects.create(
            appointment=appointment,
            report_datetime=appointment.appt_datetime,
            reason=SCHEDULED,
            subject_identifier=self.subject_identifier,
        )

    def test_requisition_form_packed_cannot_change(self):
        obj = SubjectRequisition.objects.create(
            subject_visit=self.subject_visit,
            panel=self.lab_helper.panel.panel_model_obj,
            packed=True,
            processed=True,
            received=True,
        )
        data = {"packed": False, "processed": True, "received": True}
        form = self.form_cls(data=data, instance=obj)
        form.is_valid()
        self.assertIn("packed", list(form.errors.keys()))

    def test_requisition_form_processed_can_change_if_no_aliquots(self):
        obj = SubjectRequisition.objects.create(
            subject_visit=self.subject_visit,
            panel=self.lab_helper.panel.panel_model_obj,
            packed=True,
            processed=True,
            received=True,
        )
        data = {"packed": True, "processed": False, "received": True}
        form = self.form_cls(data=data, instance=obj)
        form.is_valid()
        self.assertNotIn("processed", list(form.errors.keys()))

    def test_requisition_form_processed_cannot_change_if_aliquots(self):
        obj = SubjectRequisition.objects.create(
            subject_visit=self.subject_visit,
            panel=self.lab_helper.panel.panel_model_obj,
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
        form = self.form_cls(data=data, instance=obj)
        form.is_valid()
        self.assertIn("processed", list(form.errors.keys()))

    def test_requisition_form_received_cannot_change(self):
        obj = SubjectRequisition.objects.create(
            subject_visit=self.subject_visit,
            panel=self.lab_helper.panel.panel_model_obj,
            packed=True,
            processed=True,
            received=True,
        )
        data = {"packed": True, "processed": True, "received": False}
        form = self.form_cls(data=data, instance=obj)
        form.is_valid()
        self.assertIn("received", list(form.errors.keys()))

    def test_requisition_form_received_cannot_be_set_by_form(self):
        obj = SubjectRequisition.objects.create(
            subject_visit=self.subject_visit,
            panel=self.lab_helper.panel.panel_model_obj,
            received=False,
        )
        data = {"received": True}
        form = self.form_cls(data=data, instance=obj)
        form.is_valid()
        self.assertIn("received", list(form.errors.keys()))

    def test_requisition_form_cannot_be_changed_if_received(self):
        obj = SubjectRequisition.objects.create(
            report_datetime=self.subject_visit.report_datetime,
            subject_visit=self.subject_visit,
            panel=self.lab_helper.panel.panel_model_obj,
            received=True,
        )
        data = {"received": True}
        form = self.form_cls(data=data, instance=obj)
        form.is_valid()
        self.assertIn(
            "Requisition may not be changed", "".join(form.errors.get(NON_FIELD_ERRORS))
        )

    def test_requisition_form_dates(self):
        class RequisitionFormValidator(BaseRequisitionFormValidator):
            def validate_demographics(self):
                pass

        class RequisitionForm(RequisitionModelFormMixin, forms.ModelForm):
            form_validator_cls = RequisitionFormValidator

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
            "panel": self.lab_helper.panel.panel_model_obj,
        }
        form = RequisitionForm(data=data, instance=SubjectRequisition())
        form.is_valid()
        self.assertIn("requisition_datetime", form._errors)
        self.assertIn(
            "Invalid. Expected a date/time between", form.errors.get("requisition_datetime")[0]
        )
