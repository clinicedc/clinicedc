from datetime import datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

import time_machine
from dateutil.relativedelta import relativedelta
from django.core.exceptions import ObjectDoesNotExist
from django.forms import ValidationError
from django.test import TestCase, override_settings
from edc_consent import site_consents
from edc_constants.constants import NOT_APPLICABLE
from edc_facility.import_holidays import import_holidays
from edc_form_validators import ModelFormFieldValidatorError
from edc_metadata import KEYED, REQUIRED
from edc_metadata.models import CrfMetadata, RequisitionMetadata
from edc_reference import site_reference_configs
from edc_visit_schedule.constants import DAY01
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED
from edc_visit_tracking.model_mixins import PreviousVisitError
from edc_visit_tracking.utils import get_subject_visit_missed_model_cls

from edc_appointment.constants import (
    IN_PROGRESS_APPT,
    INCOMPLETE_APPT,
    MISSED_APPT,
    ONTIME_APPT,
    SCHEDULED_APPT,
    SKIPPED_APPT,
    UNSCHEDULED_APPT,
)
from edc_appointment.form_validators import (
    INVALID_APPT_TIMING_CRFS_EXIST,
    INVALID_APPT_TIMING_REQUISITIONS_EXIST,
    INVALID_PREVIOUS_VISIT_MISSING,
    AppointmentFormValidator,
)
from edc_appointment.form_validators.appointment_form_validator import (
    INVALID_APPT_STATUS,
    INVALID_APPT_STATUS_AT_BASELINE,
    INVALID_MISSED_APPT_NOT_ALLOWED,
    INVALID_PREVIOUS_APPOINTMENT_NOT_UPDATED,
)
from edc_appointment.models import Appointment
from edc_appointment.utils import get_previous_appointment
from edc_appointment_app.consents import v1_consent
from edc_appointment_app.models import SubjectVisit
from edc_appointment_app.visit_schedule import visit_schedule1, visit_schedule2

from ..helper import Helper
from ..test_case_mixins import AppointmentTestCaseMixin

utc_tz = ZoneInfo("UTC")


@time_machine.travel(datetime(2019, 6, 11, 8, 00, tzinfo=utc_tz))
class TestAppointmentFormValidator(AppointmentTestCaseMixin, TestCase):
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
        site_consents.registry = {}
        site_consents.register(v1_consent)
        self.helper = self.helper_cls(
            subject_identifier=self.subject_identifier,
            now=datetime(2017, 1, 7, tzinfo=ZoneInfo("UTC")),
        )
        site_reference_configs.register_from_visit_schedule(
            visit_models={"edc_appointment.appointment": "edc_appointment_app.subjectvisit"}
        )

    def test_get_previous(self):
        self.helper.consent_and_put_on_schedule()
        appointments = Appointment.objects.all()
        for i in [0, 1]:
            Appointment.objects.create(
                subject_identifier=appointments[i].subject_identifier,
                appt_datetime=appointments[i].appt_datetime + relativedelta(hours=i + 1),
                timepoint=appointments[i].timepoint,
                visit_code=appointments[i].visit_code,
                visit_code_sequence=i + 1,
                visit_schedule_name=appointments[i].visit_schedule_name,
                schedule_name=appointments[i].schedule_name,
            )
        appointments = Appointment.objects.all().order_by("timepoint", "visit_code_sequence")
        self.assertEqual(
            [f"{obj.visit_code}.{obj.visit_code_sequence}" for obj in appointments],
            ["1000.0", "1000.1", "1000.2", "2000.0", "3000.0", "4000.0"],
        )

        self.assertIsNone(get_previous_appointment(appointments[0]))

        self.assertEqual(
            appointments[4], get_previous_appointment(appointments[5], include_interim=True)
        )
        self.assertEqual(appointments[4], get_previous_appointment(appointments[5]))

        self.assertEqual(
            appointments[2], get_previous_appointment(appointments[3], include_interim=True)
        )
        self.assertEqual(appointments[0], get_previous_appointment(appointments[3]))

        self.assertEqual(
            appointments[3], get_previous_appointment(appointments[4], include_interim=True)
        )
        self.assertEqual(appointments[3], get_previous_appointment(appointments[4]))

    def test_(self):
        try:
            AppointmentFormValidator(cleaned_data={})
        except ModelFormFieldValidatorError as e:
            self.fail(f"ModelFormFieldValidatorError unexpectedly raised. Got {e}")

    def test_appointment_sequence(self):
        """Asserts a sequence error is raised if previous appointment
        is still NEW_APPT.
        """
        self.helper.consent_and_put_on_schedule()
        appointments = Appointment.objects.all()
        form_validator = AppointmentFormValidator(
            cleaned_data=dict(appt_status=IN_PROGRESS_APPT), instance=appointments[1]
        )
        with self.assertRaises(ValidationError) as cm:
            form_validator.validate()
        self.assertIn(INVALID_PREVIOUS_APPOINTMENT_NOT_UPDATED, form_validator._error_codes)
        self.assertIn("1000.0", str(cm.exception))

        form_validator = AppointmentFormValidator(
            cleaned_data=dict(appt_status=IN_PROGRESS_APPT), instance=appointments[2]
        )
        with self.assertRaises(ValidationError) as cm:
            form_validator.validate()
        self.assertIn(INVALID_PREVIOUS_APPOINTMENT_NOT_UPDATED, form_validator._error_codes)
        self.assertIn("1000.0", str(cm.exception))

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
        self.assertIn(INVALID_PREVIOUS_VISIT_MISSING, form_validator._error_codes)
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
        appointments = Appointment.objects.all().order_by("timepoint", "visit_code_sequence")

        # add continuation appt (visit_code_sequence=1)
        for i in [0, 1]:
            Appointment.objects.create(
                subject_identifier=appointments[i].subject_identifier,
                appt_datetime=appointments[i].appt_datetime + relativedelta(hours=i + 1),
                timepoint=appointments[i].timepoint,
                visit_code=appointments[i].visit_code,
                visit_code_sequence=i + 1,
                visit_schedule_name=appointments[i].visit_schedule_name,
                schedule_name=appointments[i].schedule_name,
                appt_reason=UNSCHEDULED_APPT,
            )

        appointments = Appointment.objects.all().order_by("timepoint", "visit_code_sequence")

        # appointments are
        # 1000.0, 1000.1, 1000.2 2000.0, 3000.0, 4000.0
        # NO visit reports.
        self.assertEqual(appointments[1].visit_code, "1000")
        self.assertEqual(appointments[1].visit_code_sequence, 1)

        # try to add second appt before the first
        # should fail
        form_validator = AppointmentFormValidator(
            cleaned_data=dict(appt_status=IN_PROGRESS_APPT), instance=appointments[1]
        )
        with self.assertRaises(ValidationError) as cm:
            form_validator.validate_visit_report_sequence()
        self.assertIn(INVALID_PREVIOUS_VISIT_MISSING, form_validator._error_codes)
        self.assertIn("1000.0", str(cm.exception))

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
        self.assertIn(INVALID_PREVIOUS_VISIT_MISSING, form_validator._error_codes)

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

    def test_confirm_appt_field_attrs(self):
        self.helper.consent_and_put_on_schedule()
        appointments = Appointment.objects.all().order_by("timepoint", "visit_code_sequence")
        self.assertEqual(appointments[0].visit_code, DAY01)
        self.assertEqual(appointments[0].visit_code_sequence, 0)
        self.assertEqual(appointments[0].visit_schedule_name, "visit_schedule1")
        self.assertEqual(appointments[0].schedule_name, "schedule1")
        visit_schedule = site_visit_schedules.get_visit_schedule(
            appointments[0].visit_schedule_name
        )
        schedule = visit_schedule.schedules.get(appointments[0].schedule_name)
        self.assertEqual(schedule.visits.first.timepoint, Decimal("0.0"))
        self.assertEqual(appointments[0].timepoint, Decimal("0.0"))

    def test_baseline_appt_ontime_ok(self):
        self.helper.consent_and_put_on_schedule()
        appointments = Appointment.objects.all().order_by("timepoint", "visit_code_sequence")
        form_validator = AppointmentFormValidator(
            cleaned_data=dict(
                subject_identifier=self.subject_identifier,
                appt_timing=ONTIME_APPT,
                appt_reason=SCHEDULED_APPT,
            ),
            instance=appointments[0],
        )
        try:
            form_validator.validate_appointment_timing()
        except ValidationError:
            self.fail("ValidationError unexpectedly raised")

    def test_baseline_appt_cannot_be_missed(self):
        self.helper.consent_and_put_on_schedule()
        appointments = Appointment.objects.all().order_by("timepoint", "visit_code_sequence")
        form_validator = AppointmentFormValidator(
            cleaned_data=dict(
                subject_identifier=self.subject_identifier,
                appt_timing=MISSED_APPT,
                appt_reason=SCHEDULED_APPT,
            ),
            instance=appointments[0],
        )
        with self.assertRaises(ValidationError) as cm:
            form_validator.validate_appointment_timing()
        self.assertIsNotNone(cm.exception)
        self.assertIn(INVALID_APPT_STATUS_AT_BASELINE, form_validator._error_codes)

    def test_can_miss_scheduled_appt_if_not_baseline(self):
        self.helper.consent_and_put_on_schedule()
        appointments = Appointment.objects.all().order_by("timepoint", "visit_code_sequence")
        self.assertEqual(appointments[0].appt_timing, ONTIME_APPT)
        # create report for baseline visit
        SubjectVisit.objects.create(
            appointment=appointments[0],
            report_datetime=appointments[0].appt_datetime,
            reason=SCHEDULED,
        )
        appointments[0].refresh_from_db()

        self.assertEqual(appointments[1].visit_code_sequence, 0)
        self.assertEqual(appointments[1].timepoint, Decimal("1.0"))
        form_validator = AppointmentFormValidator(
            cleaned_data=dict(
                subject_identifier=self.subject_identifier,
                appt_timing=MISSED_APPT,
                appt_reason=SCHEDULED_APPT,
            ),
            instance=appointments[1],
        )

        try:
            form_validator.validate_appointment_timing()
        except ValidationError:
            self.fail("ValidationError unexpectedly raised")

    def test_cannot_miss_unscheduled_appt(self):
        self.helper.consent_and_put_on_schedule()
        appointments = Appointment.objects.all().order_by("timepoint", "visit_code_sequence")
        self.assertEqual(appointments[0].appt_timing, ONTIME_APPT)
        # create report for baseline visit
        SubjectVisit.objects.create(
            appointment=appointments[0],
            report_datetime=appointments[0].appt_datetime,
            reason=SCHEDULED,
        )
        appointments[0].refresh_from_db()

        # create unscheduled off of baseline appt
        appointment = self.create_unscheduled_appointment(appointments[0])
        self.assertEqual(appointment.visit_code, DAY01)
        self.assertEqual(appointment.visit_code_sequence, 1)
        self.assertEqual(appointment.timepoint, Decimal("0.0"))
        form_validator = AppointmentFormValidator(
            cleaned_data=dict(
                subject_identifier=self.subject_identifier,
                appt_timing=MISSED_APPT,
                appt_reason=UNSCHEDULED_APPT,
            ),
            instance=appointment,
        )

        with self.assertRaises(ValidationError) as cm:
            form_validator.validate_appointment_timing()
        self.assertIsNotNone(cm.exception)
        self.assertIn(INVALID_MISSED_APPT_NOT_ALLOWED, form_validator._error_codes)

    @override_settings(EDC_VISIT_TRACKING_ALLOW_MISSED_UNSCHEDULED=True)
    def test_can_miss_unscheduled_appt_if_allowed_in_settings(self):
        self.helper.consent_and_put_on_schedule()
        appointments = Appointment.objects.all().order_by("timepoint", "visit_code_sequence")
        self.assertEqual(appointments[0].appt_timing, ONTIME_APPT)
        # create report for baseline visit
        SubjectVisit.objects.create(
            appointment=appointments[0],
            report_datetime=appointments[0].appt_datetime,
            reason=SCHEDULED,
        )
        appointments[0].refresh_from_db()

        # create unscheduled off of baseline appt
        appointment = self.create_unscheduled_appointment(appointments[0])
        self.assertEqual(appointment.visit_code, DAY01)
        self.assertEqual(appointment.visit_code_sequence, 1)
        self.assertEqual(appointment.timepoint, Decimal("0.0"))
        form_validator = AppointmentFormValidator(
            cleaned_data=dict(
                subject_identifier=self.subject_identifier,
                appt_timing=MISSED_APPT,
                appt_reason=UNSCHEDULED_APPT,
            ),
            instance=appointment,
        )

        try:
            form_validator.validate_appointment_timing()
        except ValidationError as e:
            self.fail(f"ValidationError unexpectedly raised. Got {e}")

    @override_settings(
        SUBJECT_VISIT_MISSED_MODEL="edc_appointment_app.subjectvisitmissed",
        SUBJECT_VISIT_MISSED_REASONS_MODEL="edc_visit_tracking.subjectvisitmissedreasons",
    )
    def test_change_from_missed_removes_missed_visit_report(self):
        self.helper.consent_and_put_on_schedule()
        appointments = Appointment.objects.all().order_by("timepoint", "visit_code_sequence")
        self.assertEqual(appointments[0].appt_timing, ONTIME_APPT)
        # create report for baseline visit
        SubjectVisit.objects.create(
            appointment=appointments[0],
            report_datetime=appointments[0].appt_datetime,
            reason=SCHEDULED,
        )
        appointments[0].refresh_from_db()

        self.assertEqual(appointments[1].visit_code_sequence, 0)
        self.assertEqual(appointments[1].timepoint, Decimal("1.0"))
        appointments[1].appt_timing = MISSED_APPT
        appointments[1].appt_reason = SCHEDULED_APPT
        appointments[1].save_base(update_fields=["appt_timing", "appt_reason"])
        appointments[1].refresh_from_db()
        subject_visit = SubjectVisit.objects.create(
            appointment=appointments[1],
            report_datetime=appointments[1].appt_datetime,
            reason=SCHEDULED,
        )

        # enter missed visit report
        get_subject_visit_missed_model_cls().objects.create(subject_visit=subject_visit)

        form_validator = AppointmentFormValidator(
            cleaned_data=dict(
                subject_identifier=self.subject_identifier,
                appt_timing=ONTIME_APPT,
                appt_reason=SCHEDULED_APPT,
            ),
            instance=appointments[1],
        )

        try:
            form_validator.validate_appointment_timing()
        except ValidationError as e:
            self.fail(f"ValidationError unexpectedly raised. Got {e}")

        # assert missed visit report removed
        try:
            get_subject_visit_missed_model_cls().objects.get(subject_visit=subject_visit)
        except ObjectDoesNotExist:
            pass
        else:
            self.fail("ObjectDoesNotExist not raised")

    @override_settings(
        SUBJECT_VISIT_MISSED_MODEL="edc_appointment_app.subjectvisitmissed",
        SUBJECT_VISIT_MISSED_REASONS_MODEL="edc_viist_tracking.subjectvisitmissedreasons",
    )
    def test_change_to_missed_not_allowed_if_crfs_exist(self):
        self.helper.consent_and_put_on_schedule()
        appointments = Appointment.objects.all().order_by("timepoint", "visit_code_sequence")
        self.assertEqual(appointments[0].appt_timing, ONTIME_APPT)
        # create report for baseline visit
        SubjectVisit.objects.create(
            appointment=appointments[0],
            report_datetime=appointments[0].appt_datetime,
            reason=SCHEDULED,
        )
        appointments[0].refresh_from_db()

        self.assertEqual(appointments[1].visit_code_sequence, 0)
        self.assertEqual(appointments[1].timepoint, Decimal("1.0"))
        appointments[1].appt_timing = ONTIME_APPT
        appointments[1].appt_reason = SCHEDULED_APPT
        appointments[1].save_base(update_fields=["appt_timing", "appt_reason"])
        appointments[1].refresh_from_db()
        subject_visit = SubjectVisit.objects.create(
            appointment=appointments[1],
            report_datetime=appointments[1].appt_datetime,
            reason=SCHEDULED,
        )

        # enter CRF
        crf_metadata = CrfMetadata.objects.create(
            model="edc_appointment.crfone",
            subject_identifier=subject_visit.subject_identifier,
            visit_schedule_name=subject_visit.visit_schedule_name,
            schedule_name=subject_visit.schedule_name,
            visit_code=subject_visit.visit_code,
            visit_code_sequence=subject_visit.visit_code_sequence,
            entry_status=KEYED,
            show_order=100,
        )

        form_validator = AppointmentFormValidator(
            cleaned_data=dict(
                subject_identifier=self.subject_identifier,
                appt_timing=MISSED_APPT,
                appt_reason=SCHEDULED_APPT,
            ),
            instance=appointments[1],
        )

        with self.assertRaises(ValidationError) as cm:
            form_validator.validate_appointment_timing()
        self.assertIsNotNone(cm.exception)
        self.assertIn(INVALID_APPT_TIMING_CRFS_EXIST, form_validator._error_codes)

        # reset CRF metadata
        crf_metadata.entry_status = REQUIRED
        crf_metadata.save()
        try:
            form_validator.validate_appointment_timing()
        except ValidationError:
            self.fail("ValidationError raised")

    @override_settings(
        SUBJECT_VISIT_MISSED_MODEL="edc_appointment_app.subjectvisitmissed",
        SUBJECT_VISIT_MISSED_REASONS_MODEL="edc_visit_tracking.subjectvisitmissedreasons",
    )
    def test_change_to_missed_not_allowed_if_requisitions_exist(self):
        self.helper.consent_and_put_on_schedule()
        appointments = Appointment.objects.all().order_by("timepoint", "visit_code_sequence")
        self.assertEqual(appointments[0].appt_timing, ONTIME_APPT)
        # create report for baseline visit
        SubjectVisit.objects.create(
            appointment=appointments[0],
            report_datetime=appointments[0].appt_datetime,
            reason=SCHEDULED,
        )
        appointments[0].refresh_from_db()

        self.assertEqual(appointments[1].visit_code_sequence, 0)
        self.assertEqual(appointments[1].timepoint, Decimal("1.0"))
        appointments[1].appt_timing = ONTIME_APPT
        appointments[1].appt_reason = SCHEDULED_APPT
        appointments[1].save_base(update_fields=["appt_timing", "appt_reason"])
        appointments[1].refresh_from_db()
        subject_visit = SubjectVisit.objects.create(
            appointment=appointments[1],
            report_datetime=appointments[1].appt_datetime,
            reason=SCHEDULED,
        )

        # enter Requisition
        requisition_metadata = RequisitionMetadata.objects.create(
            model="edc_appointment.subjectrequisition",
            panel_name="panel1",
            subject_identifier=subject_visit.subject_identifier,
            visit_schedule_name=subject_visit.visit_schedule_name,
            schedule_name=subject_visit.schedule_name,
            visit_code=subject_visit.visit_code,
            visit_code_sequence=subject_visit.visit_code_sequence,
            entry_status=KEYED,
            show_order=200,
        )

        form_validator = AppointmentFormValidator(
            cleaned_data=dict(
                subject_identifier=self.subject_identifier,
                appt_timing=MISSED_APPT,
                appt_reason=SCHEDULED_APPT,
            ),
            instance=appointments[1],
        )

        with self.assertRaises(ValidationError) as cm:
            form_validator.validate_appointment_timing()
        self.assertIsNotNone(cm.exception)
        self.assertIn(INVALID_APPT_TIMING_REQUISITIONS_EXIST, form_validator._error_codes)

        # reset Requisition metadata
        requisition_metadata.entry_status = REQUIRED
        requisition_metadata.save()
        try:
            form_validator.validate_appointment_timing()
        except ValidationError:
            self.fail("ValidationError raised")

    def test_baseline_visit_report_datetime_must_match_appt_datetime(self):
        """Baseline appt date resets starting appointment, so visit
        report must match.
        """
        self.helper.consent_and_put_on_schedule()
        appointments = Appointment.objects.all().order_by("timepoint", "visit_code_sequence")
        self.assertEqual(appointments[0].appt_timing, ONTIME_APPT)
        # create report for baseline visit
        SubjectVisit.objects.create(
            appointment=appointments[0],
            report_datetime=appointments[0].appt_datetime,
            reason=SCHEDULED,
        )

    @override_settings(
        EDC_APPOINTMENT_ALLOW_SKIPPED_APPT_USING={
            "edc_appointment_app.crfone": ("next_appt_date", "next_visit_code")
        }
    )
    def test_skipped_never_allowed_at_baseline(self):
        self.helper.consent_and_put_on_schedule()
        appointments = Appointment.objects.all().order_by("timepoint", "visit_code_sequence")
        self.assertEqual(appointments[0].appt_timing, ONTIME_APPT)
        form_validator = AppointmentFormValidator(
            cleaned_data=dict(
                subject_identifier=self.subject_identifier,
                appt_status=SKIPPED_APPT,
                appt_timing=NOT_APPLICABLE,
                appt_reason=SCHEDULED_APPT,
            ),
            instance=appointments[0],
        )
        with self.assertRaises(ValidationError) as cm:
            form_validator.validate()
        self.assertIsNotNone(cm.exception)
        self.assertIn(INVALID_APPT_STATUS_AT_BASELINE, form_validator._error_codes)

    @override_settings(
        EDC_APPOINTMENT_ALLOW_SKIPPED_APPT_USING={
            "edc_appointment_app.crfone": ("next_appt_date", "next_visit_code")
        }
    )
    def test_skipped_allowed_after_baseline_and_settings_attr_is_set(self):
        self.helper.consent_and_put_on_schedule()
        appointments = Appointment.objects.all().order_by("timepoint", "visit_code_sequence")
        SubjectVisit.objects.create(
            appointment=appointments[0],
            report_datetime=appointments[0].appt_datetime,
            reason=SCHEDULED,
        )
        appointments[0].appt_status = INCOMPLETE_APPT
        appointments[0].save()

        form_validator = AppointmentFormValidator(
            cleaned_data=dict(
                subject_identifier=self.subject_identifier,
                appt_status=SKIPPED_APPT,
                appt_timing=NOT_APPLICABLE,
                appt_reason=SCHEDULED_APPT,
            ),
            instance=appointments[1],
        )
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f"ValidationError unexpectedly raised. Got {e}")

    @override_settings(EDC_APPOINTMENT_ALLOW_SKIPPED_APPT_USING={})
    def test_skipped_not_allowed_if_settings_attr_not_set(self):
        self.helper.consent_and_put_on_schedule()
        appointments = Appointment.objects.all().order_by("timepoint", "visit_code_sequence")
        SubjectVisit.objects.create(
            appointment=appointments[0],
            report_datetime=appointments[0].appt_datetime,
            reason=SCHEDULED,
        )
        appointments[0].appt_status = INCOMPLETE_APPT
        appointments[0].save()

        form_validator = AppointmentFormValidator(
            cleaned_data=dict(
                subject_identifier=self.subject_identifier,
                appt_status=SKIPPED_APPT,
                appt_timing=NOT_APPLICABLE,
                appt_reason=SCHEDULED_APPT,
            ),
            instance=appointments[1],
        )
        with self.assertRaises(ValidationError) as cm:
            form_validator.validate()
        self.assertIsNotNone(cm.exception)
        self.assertIn(INVALID_APPT_STATUS, form_validator._error_codes)

    @override_settings(
        EDC_APPOINTMENT_ALLOW_SKIPPED_APPT_USING={
            "edc_appointment_app.crfone": ("next_appt_date", "next_visit_code")
        }
    )
    def test_skip_appointments(self):
        self.helper.consent_and_put_on_schedule()
        appointments = Appointment.objects.all().order_by("timepoint", "visit_code_sequence")
        appointments[0].appt_status = IN_PROGRESS_APPT
        appointments[0].save()
        SubjectVisit.objects.create(
            appointment=appointments[0],
            report_datetime=appointments[0].appt_datetime,
            reason=SCHEDULED,
        )
        appointments[0].refresh_from_db()
        self.assertEqual(appointments[0].appt_status, IN_PROGRESS_APPT)
