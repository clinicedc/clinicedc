from copy import deepcopy

from django import forms
from django.test import TestCase, tag
from edc_appointment.models import Appointment
from edc_constants.constants import OTHER, YES, ALIVE
from edc_facility.import_holidays import import_holidays
from edc_form_validators import REQUIRED_ERROR
from edc_reference import site_reference_configs
from edc_utils import get_utcnow
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.constants import MISSED_VISIT, UNSCHEDULED, SCHEDULED
from edc_visit_tracking.form_validators import VisitFormValidator

from ..helper import Helper
from ..models import SubjectVisit
from ..visit_schedule import visit_schedule1, visit_schedule2


class TestSubjectVisitFormValidator(TestCase):
    helper_cls = Helper

    @classmethod
    def setUpClass(cls):
        import_holidays()
        return super(TestSubjectVisitFormValidator, cls).setUpClass()

    def setUp(self):
        self.subject_identifier = "12345"
        self.helper = self.helper_cls(subject_identifier=self.subject_identifier)
        site_visit_schedules._registry = {}
        site_visit_schedules.register(visit_schedule=visit_schedule1)
        site_visit_schedules.register(visit_schedule=visit_schedule2)
        site_reference_configs.register_from_visit_schedule(
            visit_models={
                "edc_appointment.appointment": "edc_visit_tracking.subjectvisit"
            }
        )
        self.helper.consent_and_put_on_schedule()
        self.appointment = Appointment.objects.all().order_by("timepoint_datetime")[0]

    def test_form_validator_ok(self):
        self.helper.consent_and_put_on_schedule()
        appointment = Appointment.objects.all()[0]
        subject_visit = SubjectVisit.objects.create(
            appointment=appointment, reason=SCHEDULED
        )
        cleaned_data = dict(
            appointment=appointment,
            reason=SCHEDULED,
            is_present=YES,
            survival_status=ALIVE,
            last_alive_date=get_utcnow().date(),
        )
        form_validator = VisitFormValidator(
            cleaned_data=cleaned_data, instance=subject_visit
        )
        form_validator.validate()

    def test_visit_code_reason_with_visit_code_sequence_0(self):
        cleaned_data = {"appointment": self.appointment, "reason": UNSCHEDULED}
        form_validator = VisitFormValidator(cleaned_data=cleaned_data)
        try:
            form_validator.validate()
        except forms.ValidationError:
            pass
        self.assertIn("reason", form_validator._errors)

    def test_visit_code_reason_with_visit_code_sequence_1(self):
        SubjectVisit.objects.create(appointment=self.appointment, reason=SCHEDULED)

        opts = self.appointment.__dict__
        opts.pop("_state")
        opts.pop("id")
        opts.pop("created")
        opts.pop("modified")
        opts["visit_code_sequence"] = 1
        appointment = Appointment.objects.create(**opts)

        cleaned_data = {"appointment": appointment, "reason": SCHEDULED}
        form_validator = VisitFormValidator(cleaned_data=cleaned_data)
        try:
            form_validator.validate()
        except forms.ValidationError:
            pass
        self.assertIn("reason", form_validator._errors)

    def test_visit_code_reason_with_visit_code_sequence_2(self):
        SubjectVisit.objects.create(appointment=self.appointment, reason=SCHEDULED)

        opts = self.appointment.__dict__
        opts.pop("_state")
        opts.pop("id")
        opts.pop("created")
        opts.pop("modified")
        opts["visit_code_sequence"] = 1
        Appointment.objects.create(**opts)
        opts["visit_code_sequence"] = 2
        appointment = Appointment.objects.create(**opts)

        cleaned_data = {"appointment": appointment, "reason": SCHEDULED}
        form_validator = VisitFormValidator(cleaned_data=cleaned_data)
        try:
            form_validator.validate()
        except forms.ValidationError:
            pass
        self.assertIn(
            "Previous visit report required",
            ",".join([str(e) for e in form_validator._errors.values()]),
        )
        self.assertIn(
            "1000.1", ",".join([str(e) for e in form_validator._errors.values()])
        )

    def test_reason_missed(self):
        options = {
            "appointment": self.appointment,
            "reason": MISSED_VISIT,
            "reason_missed": None,
        }
        form_validator = VisitFormValidator(cleaned_data=options)
        try:
            form_validator.validate()
        except forms.ValidationError:
            pass
        self.assertIn("reason_missed", form_validator._errors)

    def test_reason_unscheduled(self):
        SubjectVisit.objects.create(appointment=self.appointment, reason=SCHEDULED)

        # create unscheduled appointment (XXXX.1)
        opts = self.appointment.__dict__
        opts.pop("_state")
        opts.pop("id")
        opts.pop("created")
        opts.pop("modified")
        opts["visit_code_sequence"] = 1
        appointment = Appointment.objects.create(**opts)
        # start subject visit form with unscheduled appointment
        options = {
            "appointment": appointment,
            "reason": UNSCHEDULED,
            "reason_unscheduled": None,
        }
        form_validator = VisitFormValidator(cleaned_data=options)
        try:
            form_validator.validate()
        except forms.ValidationError:
            pass
        self.assertIn("reason_unscheduled", form_validator._errors)
        self.assertIn(REQUIRED_ERROR, form_validator._error_codes)

    def test_reason_unscheduled_other(self):
        SubjectVisit.objects.create(appointment=self.appointment, reason=SCHEDULED)

        opts = self.appointment.__dict__
        opts.pop("_state")
        opts.pop("id")
        opts.pop("created")
        opts.pop("modified")
        opts["visit_code_sequence"] = 1
        appointment = Appointment.objects.create(**opts)

        options = {
            "appointment": appointment,
            "reason": UNSCHEDULED,
            "reason_unscheduled": OTHER,
            "reason_unscheduled_other": None,
        }
        form_validator = VisitFormValidator(cleaned_data=options)
        try:
            form_validator.validate()
        except forms.ValidationError:
            pass
        self.assertIn("reason_unscheduled_other", form_validator._errors)
        self.assertIn(REQUIRED_ERROR, form_validator._error_codes)

    def test_info_source_other(self):
        options = {
            "appointment": self.appointment,
            "info_source": OTHER,
            "info_source_other": None,
        }
        form_validator = VisitFormValidator(cleaned_data=options)
        try:
            form_validator.validate()
        except forms.ValidationError:
            pass
        self.assertIn("info_source_other", form_validator._errors)
        self.assertIn(REQUIRED_ERROR, form_validator._error_codes)
