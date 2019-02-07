from arrow import arrow
from datetime import datetime
from dateutil.relativedelta import relativedelta
from decimal import Decimal
from django.forms import ValidationError
from django.test import TestCase
from edc_facility.import_holidays import import_holidays
from edc_form_validators import ModelFormFieldValidatorError
from edc_visit_schedule import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED
from edc_visit_tracking.model_mixins import PreviousVisitError

from ..constants import IN_PROGRESS_APPT
from ..form_validators import AppointmentFormValidator
from ..models import Appointment
from .helper import Helper
from .models import SubjectVisit
from .visit_schedule import visit_schedule1, visit_schedule2


class TestAppointmentForm(TestCase):

    helper_cls = Helper

    @classmethod
    def setUpClass(cls):
        import_holidays()
        return super().setUpClass()

    def setUp(self):
        self.subject_identifier = "12345"
        site_visit_schedules._registry = {}
        site_visit_schedules.register(visit_schedule=visit_schedule1)
        site_visit_schedules.register(visit_schedule=visit_schedule2)
        self.helper = self.helper_cls(
            subject_identifier=self.subject_identifier,
            now=arrow.Arrow.fromdatetime(datetime(2017, 1, 7), tzinfo="UTC").datetime,
        )

    def test_get_previous(self):
        self.helper.consent_and_put_on_schedule()
        appointments = Appointment.objects.all()
        for i in [0, 1]:
            Appointment.objects.create(
                subject_identifier=appointments[i].subject_identifier,
                appt_datetime=appointments[i].appt_datetime
                + relativedelta(hours=i + 1),
                timepoint=appointments[i].timepoint + Decimal(str(i / 10)),
                visit_code=appointments[i].visit_code,
                visit_code_sequence=i + 1,
                visit_schedule_name=appointments[i].visit_schedule_name,
                schedule_name=appointments[i].schedule_name,
            )
        appointments = Appointment.objects.all().order_by(
            "timepoint", "visit_code_sequence"
        )
        self.assertEqual(
            [f"{obj.visit_code}.{obj.visit_code_sequence}" for obj in appointments],
            ["1000.0", "1000.1", "1000.2", "2000.0", "3000.0", "4000.0"],
        )

        self.assertIsNone(appointments[0].get_previous())
        self.assertEqual(appointments[4], appointments[5].get_previous())
        self.assertEqual(appointments[0], appointments[3].get_previous())
        self.assertEqual(
            appointments[0], appointments[1].get_previous(include_interim=True)
        )
        self.assertEqual(
            appointments[1], appointments[2].get_previous(include_interim=True)
        )
        self.assertEqual(
            appointments[2], appointments[3].get_previous(include_interim=True)
        )

    def test_(self):
        try:
            AppointmentFormValidator(cleaned_data={})
        except ModelFormFieldValidatorError as e:
            self.fail(f"ModelFormFieldValidatorError unexpectedly raised. Got {e}")

    def test_visit_report_sequence(self):
        """Asserts a sequence error is raised if previous visit
        not complete for an in progress appointment.
        """
        self.helper.consent_and_put_on_schedule()
        appointments = Appointment.objects.all()

        # try to add second appt before the first
        # should fail
        form_validator = AppointmentFormValidator(
            cleaned_data=dict(appt_status=IN_PROGRESS_APPT), instance=appointments[1]
        )
        with self.assertRaises(ValidationError) as cm:
            form_validator.validate_visit_report_sequence()
        self.assertEqual(cm.exception.code, "previous_visit_missing")
        self.assertIn("1000.0", str(cm.exception))

        # try to add second appt where first visit report is complete
        # should succeed
        # add a visit 0
        SubjectVisit.objects.create(
            appointment=appointments[0],
            report_datetime=appointments[0].appt_datetime,
            reason=SCHEDULED,
        )
        form_validator = AppointmentFormValidator(
            cleaned_data=dict(appt_status=IN_PROGRESS_APPT), instance=appointments[1]
        )
        try:
            form_validator.validate_visit_report_sequence()
        except ValidationError:
            self.fail("ValidationError unexpectedly raised.")

        # try to manually add a visit 2 before visit 1
        # should fail
        self.assertRaises(
            PreviousVisitError,
            SubjectVisit.objects.create,
            appointment=appointments[2],
            report_datetime=appointments[2].appt_datetime,
            reason=SCHEDULED,
        )

    def test_visit_report_sequence2(self):
        """Asserts a sequence error is raised if previous visit
        not complete for an in progress appointment.

        Validate the visit_code_sequence
        """
        self.helper.consent_and_put_on_schedule()
        appointments = Appointment.objects.all().order_by(
            "timepoint", "visit_code_sequence"
        )

        # add continuation appt (visit_code_sequence=1)
        for i in [0, 1]:
            Appointment.objects.create(
                subject_identifier=appointments[i].subject_identifier,
                appt_datetime=appointments[i].appt_datetime
                + relativedelta(hours=i + 1),
                timepoint=appointments[i].timepoint + Decimal(str(i / 10)),
                visit_code=appointments[i].visit_code,
                visit_code_sequence=i + 1,
                visit_schedule_name=appointments[i].visit_schedule_name,
                schedule_name=appointments[i].schedule_name,
            )

        appointments = Appointment.objects.all().order_by(
            "timepoint", "visit_code_sequence"
        )

        # appointments is
        # 1000.0, 1000.1, 1000.2 2000.0, 3000.0, 4000.0
        # no visit reports

        self.assertEqual(appointments[1].visit_code, "1000")
        self.assertEqual(appointments[1].visit_code_sequence, 1)

        # try to add second appt before the first
        # should fail
        form_validator = AppointmentFormValidator(
            cleaned_data=dict(appt_status=IN_PROGRESS_APPT), instance=appointments[1]
        )
        with self.assertRaises(ValidationError) as cm:
            form_validator.validate_visit_report_sequence()
        self.assertIn("1000.0", str(cm.exception))
        self.assertEqual(cm.exception.code, "previous_visit_missing")

        SubjectVisit.objects.create(
            appointment=appointments[0],
            report_datetime=appointments[0].appt_datetime,
            reason=SCHEDULED,
        )

        # 1000.0 (reported), 1000.1, 1000.2 2000.0, 3000.0, 4000.0
        # try to add 1000.2
        # should fail because 1000.1 not reported

        form_validator = AppointmentFormValidator(
            cleaned_data=dict(appt_status=IN_PROGRESS_APPT), instance=appointments[2]
        )
        with self.assertRaises(ValidationError) as cm:
            form_validator.validate_visit_report_sequence()
        self.assertIn("1000.1", str(cm.exception))
        self.assertEqual(cm.exception.code, "previous_visit_missing")

        SubjectVisit.objects.create(
            appointment=appointments[1],
            report_datetime=appointments[1].appt_datetime,
            reason=SCHEDULED,
        )

        form_validator = AppointmentFormValidator(
            cleaned_data=dict(appt_status=IN_PROGRESS_APPT), instance=appointments[2]
        )
        try:
            form_validator.validate_visit_report_sequence()
        except ValidationError:
            self.fail("ValidationError unexpectedly raised.")

    def test_interim_sequence(self):
        self.helper.consent_and_put_on_schedule()

        form_validator = AppointmentFormValidator(
            cleaned_data=dict(
                subject_identifier=self.subject_identifier,
                appt_status=IN_PROGRESS_APPT,
                visit_code="1000",
                visit_code_sequence=1,
                timepoint=Decimal("0.1"),
            )
        )
        form_validator.validate_visit_report_sequence()
