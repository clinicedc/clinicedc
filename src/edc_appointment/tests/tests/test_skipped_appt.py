from datetime import datetime
from zoneinfo import ZoneInfo

import time_machine
from dateutil.relativedelta import relativedelta
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase, override_settings, tag
from edc_consent import site_consents
from edc_facility import import_holidays
from edc_reference import site_reference_configs
from edc_visit_schedule.apps import populate_visit_schedule
from edc_visit_schedule.models import VisitSchedule
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED

from edc_appointment.constants import (
    COMPLETE_APPT,
    IN_PROGRESS_APPT,
    INCOMPLETE_APPT,
    NEW_APPT,
    SKIPPED_APPT,
)
from edc_appointment.models import Appointment
from edc_appointment.skip_appointments import (
    SkipAppointmentsFieldError,
    SkipAppointmentsValueError,
)
from edc_appointment.tests.helper import Helper
from edc_appointment.tests.test_case_mixins import AppointmentTestCaseMixin
from edc_appointment.utils import get_allow_skipped_appt_using
from edc_appointment_app.consents import v1_consent
from edc_appointment_app.forms import CrfThreeForm
from edc_appointment_app.models import (
    CrfFive,
    CrfFour,
    CrfOne,
    CrfThree,
    CrfTwo,
    SubjectVisit,
)
from edc_appointment_app.visit_schedule import (
    visit_schedule1,
    visit_schedule2,
    visit_schedule5,
)

utc = ZoneInfo("UTC")


@tag("2")
@time_machine.travel(datetime(2019, 6, 11, 8, 00, tzinfo=utc))
class TestSkippedAppt(AppointmentTestCaseMixin, TestCase):
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
        site_visit_schedules.register(visit_schedule=visit_schedule5)
        site_consents.registry = {}
        site_consents.register(v1_consent)
        self.helper = self.helper_cls(
            subject_identifier=self.subject_identifier,
            now=datetime(2017, 6, 5, 8, 0, 0, tzinfo=utc),
        )
        site_reference_configs.register_from_visit_schedule(
            visit_models={"edc_appointment.appointment": "edc_appointment_app.subjectvisit"}
        )
        populate_visit_schedule()

    @override_settings(
        EDC_APPOINTMENT_ALLOW_SKIPPED_APPT_USING={
            "edc_appointment_app.crfone": ("next_appt_date", "next_visit_code")
        }
    )
    def test_skip_appointments_using_crf_date(self):
        self.helper.consent_and_put_on_schedule()
        appointments = Appointment.objects.all().order_by("timepoint", "visit_code_sequence")
        appointments[0].appt_status = IN_PROGRESS_APPT
        appointments[0].save()
        subject_visit = SubjectVisit.objects.create(
            appointment=appointments[0],
            report_datetime=appointments[0].appt_datetime,
            reason=SCHEDULED,
        )
        appointments[0].refresh_from_db()
        self.assertEqual(appointments[0].appt_status, IN_PROGRESS_APPT)

        self.assertRaises(
            SkipAppointmentsValueError,
            CrfOne.objects.create,
            subject_visit=subject_visit,
            next_appt_date=subject_visit.report_datetime + relativedelta(weeks=3),
        )
        CrfOne.objects.all().delete()

        CrfOne.objects.create(
            subject_visit=subject_visit,
            next_appt_date=subject_visit.report_datetime + relativedelta(weeks=3),
            next_visit_code=appointments[3].visit_code,
        )

        appointments = Appointment.objects.all().order_by("timepoint", "visit_code_sequence")

        self.assertEqual(appointments[0].appt_status, IN_PROGRESS_APPT)
        self.assertEqual(appointments[1].appt_status, SKIPPED_APPT)

    @override_settings(
        EDC_APPOINTMENT_ALLOW_SKIPPED_APPT_USING={
            "edc_appointment_app.crfone": ("next_appt_date", "next_visit_code"),
            "edc_appointment_app.crftwo": ("report_datetime", "next_visit_code"),
            "edc_appointment_app.crfthree": ("report_datetime", "f1"),
            "edc_appointment_app.crffour": ("report_datetime", "next_visit_code"),
        }
    )
    def test_settings_improperly_configured(self):
        self.assertRaises(ImproperlyConfigured, get_allow_skipped_appt_using)

    @override_settings(
        EDC_APPOINTMENT_ALLOW_SKIPPED_APPT_USING={
            "edc_appointment_app.crftwo": ("report_datetime", "next_visit_code_blah"),
        }
    )
    def test_skip_appointments_using_bad_settings_for_crf(self):
        self.helper.consent_and_put_on_schedule()
        appointments = Appointment.objects.all().order_by("timepoint", "visit_code_sequence")
        appointments[0].appt_status = IN_PROGRESS_APPT
        appointments[0].save()
        subject_visit = SubjectVisit.objects.create(
            appointment=appointments[0],
            report_datetime=appointments[0].appt_datetime,
            reason=SCHEDULED,
        )
        appointments[0].refresh_from_db()
        self.assertEqual(appointments[0].appt_status, IN_PROGRESS_APPT)

        # next_visit_code_blah is not a valid field on Crf
        self.assertRaises(
            SkipAppointmentsFieldError,
            CrfTwo.objects.create,
            subject_visit=subject_visit,
            report_datetime=subject_visit.report_datetime,
        )

    @override_settings(
        EDC_APPOINTMENT_ALLOW_SKIPPED_APPT_USING={
            "edc_appointment_app.crftwo": ("report_datetime_blah", "f1"),
        }
    )
    def test_skip_appointments_using_bad_settings_for_crf2(self):
        self.helper.consent_and_put_on_schedule()
        appointments = Appointment.objects.all().order_by("timepoint", "visit_code_sequence")
        appointments[0].appt_status = IN_PROGRESS_APPT
        appointments[0].save()
        subject_visit = SubjectVisit.objects.create(
            appointment=appointments[0],
            report_datetime=appointments[0].appt_datetime,
            reason=SCHEDULED,
        )
        appointments[0].refresh_from_db()
        self.assertEqual(appointments[0].appt_status, IN_PROGRESS_APPT)

        # report_datetime_blah is not a valid field on Crf
        self.assertRaises(
            SkipAppointmentsFieldError,
            CrfTwo.objects.create,
            subject_visit=subject_visit,
            report_datetime=subject_visit.report_datetime,
            f1=appointments[3].visit_code,
        )

    @override_settings(
        EDC_APPOINTMENT_ALLOW_SKIPPED_APPT_USING={
            "edc_appointment_app.crfthree": ("report_datetime", "f1"),
        }
    )
    def test_skip_appointments_using_crf_ok(self):
        self.helper.consent_and_put_on_schedule()
        appointments = Appointment.objects.all().order_by("timepoint", "visit_code_sequence")
        appointments[0].appt_status = IN_PROGRESS_APPT
        appointments[0].save()
        subject_visit = SubjectVisit.objects.create(
            appointment=appointments[0],
            report_datetime=appointments[0].appt_datetime,
            reason=SCHEDULED,
        )
        appointments[0].refresh_from_db()
        self.assertEqual(appointments[0].appt_status, IN_PROGRESS_APPT)
        try:
            CrfThree.objects.create(
                subject_visit=subject_visit,
                report_datetime=appointments[3].appt_datetime,
                f1=appointments[3].visit_code,
            )
        except SkipAppointmentsValueError as e:
            self.fail(f"SkipAppointmentsValueError unexpectedly raised. Got {e}")
        except SkipAppointmentsFieldError as e:
            self.fail(f"SkipAppointmentsFieldError unexpectedly raised. Got {e}")

    @override_settings(
        EDC_APPOINTMENT_ALLOW_SKIPPED_APPT_USING={
            "edc_appointment_app.crfthree": ("report_datetime", "f1"),
        }
    )
    def test_skip_multiple_appointments_using_good_crf(self):
        self.helper.consent_and_put_on_schedule()
        appointments = Appointment.objects.all().order_by("timepoint", "visit_code_sequence")
        appointments[0].appt_status = IN_PROGRESS_APPT
        appointments[0].save()
        subject_visit = SubjectVisit.objects.create(
            appointment=appointments[0],
            report_datetime=appointments[0].appt_datetime,
            reason=SCHEDULED,
        )
        appointments[0].refresh_from_db()

        CrfThree.objects.create(
            subject_visit=subject_visit,
            report_datetime=appointments[3].appt_datetime,
            f1=appointments[3].visit_code,
        )
        appointments = Appointment.objects.all().order_by("timepoint", "visit_code_sequence")
        self.assertEqual(appointments[1].appt_status, SKIPPED_APPT)
        self.assertEqual(appointments[2].appt_status, SKIPPED_APPT)
        self.assertEqual(appointments[3].appt_status, NEW_APPT)

    @override_settings(
        EDC_APPOINTMENT_ALLOW_SKIPPED_APPT_USING={
            "edc_appointment_app.crfthree": ("appt_date", "f1"),
        }
    )
    def test_skip_multiple_appointments_using_last_crf(self):
        self.helper.consent_and_put_on_schedule()
        appointments = Appointment.objects.all().order_by("timepoint", "visit_code_sequence")
        appointments[0].appt_status = IN_PROGRESS_APPT
        appointments[0].save()
        subject_visit = SubjectVisit.objects.create(
            appointment=appointments[0],
            report_datetime=appointments[0].appt_datetime,
            reason=SCHEDULED,
        )
        CrfThree.objects.create(
            subject_visit=subject_visit,
            appt_date=appointments[2].appt_datetime.date(),
            f1=appointments[2].visit_code,
        )

        appointments = Appointment.objects.all().order_by("timepoint", "visit_code_sequence")
        self.assertEqual(appointments[0].appt_status, IN_PROGRESS_APPT)
        self.assertEqual(appointments[1].appt_status, SKIPPED_APPT)
        self.assertEqual(appointments[2].appt_status, NEW_APPT)
        self.assertEqual(appointments[3].appt_status, NEW_APPT)

        appointments[1].appt_status = IN_PROGRESS_APPT
        appointments[1].save()
        subject_visit = SubjectVisit.objects.create(
            appointment=appointments[1],
            report_datetime=appointments[1].appt_datetime,
            reason=SCHEDULED,
        )
        CrfThree.objects.create(
            subject_visit=subject_visit,
            f1=appointments[3].visit_code,
            appt_date=appointments[3].appt_datetime.date(),
        )

        appointments = Appointment.objects.all().order_by("timepoint", "visit_code_sequence")
        self.assertEqual(appointments[0].appt_status, INCOMPLETE_APPT)
        self.assertEqual(appointments[1].appt_status, IN_PROGRESS_APPT)
        self.assertEqual(appointments[2].appt_status, SKIPPED_APPT)
        self.assertEqual(appointments[3].appt_status, NEW_APPT)

    @override_settings(
        EDC_APPOINTMENT_ALLOW_SKIPPED_APPT_USING={
            "edc_appointment_app.crftwo": ("report_datetime", "visitschedule"),
        }
    )
    def test_visit_code_as_visit_schedule_fk_ok(self):
        self.helper.consent_and_put_on_schedule()
        appointments = Appointment.objects.all().order_by("timepoint", "visit_code_sequence")
        appointments[0].appt_status = IN_PROGRESS_APPT
        appointments[0].save()
        subject_visit = SubjectVisit.objects.create(
            appointment=appointments[0],
            report_datetime=appointments[0].appt_datetime,
            reason=SCHEDULED,
        )
        self.assertRaises(
            SkipAppointmentsValueError,
            CrfTwo.objects.create,
            subject_visit=subject_visit,
            report_datetime=appointments[1].appt_datetime,
            visitschedule=VisitSchedule.objects.get(visit_code=appointments[3].visit_code),
        )

        self.assertRaises(
            SkipAppointmentsValueError,
            CrfTwo.objects.create,
            subject_visit=subject_visit,
            report_datetime=appointments[3].appt_datetime,
            visitschedule=VisitSchedule.objects.get(visit_code=appointments[1].visit_code),
        )

    @tag("1")
    @override_settings(
        EDC_APPOINTMENT_ALLOW_SKIPPED_APPT_USING={
            "edc_appointment_app.crfthree": ("appt_date", "f1"),
        }
    )
    def test_last_crf_with_absurd_date_relative_to_visit_code(self):
        self.helper.consent_and_put_on_schedule()
        appointments = Appointment.objects.all().order_by("timepoint", "visit_code_sequence")
        appointments[0].appt_status = IN_PROGRESS_APPT
        appointments[0].save()
        subject_visit = SubjectVisit.objects.create(
            appointment=appointments[0],
            report_datetime=appointments[0].appt_datetime,
            reason=SCHEDULED,
        )
        self.assertRaises(
            SkipAppointmentsValueError,
            CrfThree.objects.create,
            subject_visit=subject_visit,
            appt_date=appointments[1].appt_datetime.date(),
            f1=appointments[3].visit_code,
        )

    @override_settings(
        EDC_APPOINTMENT_ALLOW_SKIPPED_APPT_USING={
            "edc_appointment_app.crfthree": ("appt_date", "f1"),
        }
    )
    def test_delete(self):
        self.helper.consent_and_put_on_schedule()
        appointments = Appointment.objects.all().order_by("timepoint", "visit_code_sequence")
        appointments[0].appt_status = IN_PROGRESS_APPT
        appointments[0].save()
        subject_visit = SubjectVisit.objects.create(
            appointment=appointments[0],
            report_datetime=appointments[0].appt_datetime,
            reason=SCHEDULED,
        )
        crf_three_1000 = CrfThree.objects.create(
            subject_visit=subject_visit,
            appt_date=appointments[2].appt_datetime.date(),
            f1=appointments[2].visit_code,
        )
        appointments = Appointment.objects.all().order_by("timepoint", "visit_code_sequence")
        appointments[1].appt_status = IN_PROGRESS_APPT
        appointments[1].save()
        subject_visit = SubjectVisit.objects.create(
            appointment=appointments[1],
            report_datetime=appointments[1].appt_datetime,
            reason=SCHEDULED,
        )
        crf_three_2000 = CrfThree.objects.create(
            subject_visit=subject_visit,
            f1=appointments[3].visit_code,
            appt_date=appointments[3].appt_datetime.date(),
        )
        appointments = Appointment.objects.all().order_by("timepoint", "visit_code_sequence")
        self.assertEqual(appointments[0].appt_status, INCOMPLETE_APPT)
        self.assertEqual(appointments[1].appt_status, IN_PROGRESS_APPT)
        self.assertEqual(appointments[2].appt_status, SKIPPED_APPT)
        self.assertEqual(appointments[3].appt_status, NEW_APPT)

        crf_three_2000.delete()
        appointments = Appointment.objects.all().order_by("timepoint", "visit_code_sequence")
        self.assertEqual(appointments[0].appt_status, INCOMPLETE_APPT)
        self.assertEqual(appointments[1].appt_status, IN_PROGRESS_APPT)
        self.assertEqual(appointments[2].appt_status, NEW_APPT)
        self.assertEqual(appointments[3].appt_status, NEW_APPT)

        crf_three_1000.delete()
        appointments = Appointment.objects.all().order_by("timepoint", "visit_code_sequence")
        self.assertEqual(appointments[0].appt_status, INCOMPLETE_APPT)
        self.assertEqual(appointments[1].appt_status, IN_PROGRESS_APPT)
        self.assertEqual(appointments[2].appt_status, NEW_APPT)
        self.assertEqual(appointments[3].appt_status, NEW_APPT)

    @override_settings(
        EDC_APPOINTMENT_ALLOW_SKIPPED_APPT_USING={
            "edc_appointment_app.crfthree": ("appt_date", "f1"),
        }
    )
    def test_skip2(self):
        self.helper.consent_and_put_on_schedule(
            visit_schedule_name="visit_schedule5", schedule_name="monthly_schedule"
        )
        appointments = Appointment.objects.all().order_by("timepoint", "visit_code_sequence")
        appointments[0].appt_status = IN_PROGRESS_APPT
        appointments[0].save()
        subject_visit = SubjectVisit.objects.create(
            appointment=appointments[0],
            report_datetime=appointments[0].appt_datetime,
            reason=SCHEDULED,
        )

        appointments = Appointment.objects.all().order_by("timepoint", "visit_code_sequence")
        self.assertEqual(appointments[0].appt_status, IN_PROGRESS_APPT)
        self.assertEqual(appointments[1].appt_status, NEW_APPT)

        for model_cls in [CrfOne, CrfTwo, CrfFour, CrfFive]:
            model_cls.objects.create(
                subject_visit=subject_visit,
                report_datetime=appointments[0].appt_datetime,
                f1="blah",
            )
        appointments = Appointment.objects.all().order_by("timepoint", "visit_code_sequence")
        self.assertEqual(appointments[0].appt_status, IN_PROGRESS_APPT)
        self.assertEqual(appointments[1].appt_status, NEW_APPT)
        CrfThree.objects.create(
            subject_visit=subject_visit,
            report_datetime=subject_visit.report_datetime,
            appt_date=appointments[2].appt_datetime.date(),
            f1=appointments[2].visit_code,
        )
        appointments = Appointment.objects.all().order_by("timepoint", "visit_code_sequence")
        self.assertEqual(appointments[0].appt_status, IN_PROGRESS_APPT)
        self.assertEqual(appointments[1].appt_status, SKIPPED_APPT)
        self.assertEqual(appointments[2].appt_status, NEW_APPT)
        self.assertEqual(appointments[3].appt_status, NEW_APPT)
        self.assertEqual(appointments[4].appt_status, NEW_APPT)
        self.assertEqual(appointments[5].appt_status, NEW_APPT)
        self.assertEqual(appointments[6].appt_status, NEW_APPT)

        appointments[2].appt_status = IN_PROGRESS_APPT
        appointments[2].save()
        subject_visit = SubjectVisit.objects.create(
            appointment=appointments[2],
            report_datetime=appointments[2].appt_datetime,
            reason=SCHEDULED,
        )

        appointments = Appointment.objects.all().order_by("timepoint", "visit_code_sequence")
        self.assertEqual(appointments[0].appt_status, COMPLETE_APPT)
        self.assertEqual(appointments[1].appt_status, SKIPPED_APPT)
        self.assertEqual(appointments[2].appt_status, IN_PROGRESS_APPT)

        for model_cls in [CrfOne, CrfTwo, CrfFour, CrfFive]:
            model_cls.objects.create(
                subject_visit=subject_visit,
                report_datetime=appointments[2].appt_datetime,
                f1="blah",
            )

        appointments = Appointment.objects.all().order_by("timepoint", "visit_code_sequence")
        self.assertEqual(appointments[0].appt_status, COMPLETE_APPT)
        self.assertEqual(appointments[1].appt_status, SKIPPED_APPT)
        self.assertEqual(appointments[2].appt_status, IN_PROGRESS_APPT)

        CrfThree.objects.create(
            subject_visit=subject_visit,
            report_datetime=subject_visit.report_datetime,
            appt_date=appointments[3].appt_datetime.date(),
            f1=appointments[3].visit_code,
        )

        appointments = Appointment.objects.all().order_by("timepoint", "visit_code_sequence")
        self.assertEqual(appointments[0].appt_status, COMPLETE_APPT)
        self.assertEqual(appointments[1].appt_status, SKIPPED_APPT)
        self.assertEqual(appointments[2].appt_status, IN_PROGRESS_APPT)

        appointments = Appointment.objects.all().order_by("timepoint", "visit_code_sequence")
        appointments[2].appt_status = COMPLETE_APPT
        appointments[2].save()
        appointments = Appointment.objects.all().order_by("timepoint", "visit_code_sequence")
        self.assertEqual(appointments[0].appt_status, COMPLETE_APPT)
        self.assertEqual(appointments[1].appt_status, SKIPPED_APPT)
        self.assertEqual(appointments[2].appt_status, IN_PROGRESS_APPT)
        self.assertEqual(appointments[3].appt_status, NEW_APPT)
        self.assertEqual(appointments[4].appt_status, NEW_APPT)
        self.assertEqual(appointments[5].appt_status, NEW_APPT)
        self.assertEqual(appointments[6].appt_status, NEW_APPT)

        appointments[3].appt_status = IN_PROGRESS_APPT
        appointments[3].save()
        subject_visit = SubjectVisit.objects.create(
            appointment=appointments[3],
            report_datetime=appointments[3].appt_datetime,
            reason=SCHEDULED,
        )
        CrfOne.objects.create(
            subject_visit=subject_visit,
            report_datetime=subject_visit.report_datetime,
            f1="blah",
        )
        CrfThree.objects.create(
            subject_visit=subject_visit,
            report_datetime=subject_visit.report_datetime,
            appt_date=appointments[6].appt_datetime.date(),
            f1=appointments[6].visit_code,
        )

        appointments = Appointment.objects.all().order_by("timepoint", "visit_code_sequence")
        self.assertEqual(appointments[0].appt_status, COMPLETE_APPT)
        self.assertEqual(appointments[1].appt_status, SKIPPED_APPT)
        self.assertEqual(appointments[2].appt_status, COMPLETE_APPT)
        self.assertEqual(appointments[3].appt_status, IN_PROGRESS_APPT)
        self.assertEqual(appointments[4].appt_status, SKIPPED_APPT)
        self.assertEqual(appointments[5].appt_status, SKIPPED_APPT)
        self.assertEqual(appointments[6].appt_status, NEW_APPT)

        appointments[0].appt_status = IN_PROGRESS_APPT
        appointments[0].save()
        subject_visit = SubjectVisit.objects.get(appointment=appointments[0])
        subject_visit.save()
        CrfThree.objects.create(
            subject_visit=subject_visit,
            report_datetime=subject_visit.report_datetime,
            appt_date=appointments[2].appt_datetime.date(),
            f1=appointments[2].visit_code,
        )
        appointments = Appointment.objects.all().order_by("timepoint", "visit_code_sequence")
        self.assertEqual(appointments[0].appt_status, IN_PROGRESS_APPT)
        self.assertEqual(appointments[1].appt_status, SKIPPED_APPT)
        self.assertEqual(appointments[2].appt_status, COMPLETE_APPT)
        self.assertEqual(appointments[3].appt_status, INCOMPLETE_APPT)
        self.assertEqual(appointments[4].appt_status, SKIPPED_APPT)
        self.assertEqual(appointments[5].appt_status, SKIPPED_APPT)
        self.assertEqual(appointments[6].appt_status, NEW_APPT)

    @tag("7")
    # @time_machine.travel(datetime(2021, 10, 6, 8, 00, tzinfo=utc))
    @override_settings(
        EDC_APPOINTMENT_ALLOW_SKIPPED_APPT_USING={
            "edc_appointment_app.crfthree": ("appt_date", "f1"),
        }
    )
    def test_when_next_appointment_in_window(self):
        self.helper.consent_and_put_on_schedule(
            visit_schedule_name="visit_schedule5", schedule_name="monthly_schedule"
        )
        appointments = Appointment.objects.all().order_by("timepoint", "visit_code_sequence")
        appointments[0].appt_status = IN_PROGRESS_APPT
        appointments[0].save()
        subject_visit = SubjectVisit.objects.create(
            appointment=appointments[0],
            report_datetime=appointments[0].appt_datetime,
            reason=SCHEDULED,
        )

        appointments = Appointment.objects.all().order_by("timepoint", "visit_code_sequence")
        for model_cls in [CrfOne, CrfTwo, CrfFour, CrfFive]:
            model_cls.objects.create(
                subject_visit=subject_visit,
                report_datetime=appointments[0].appt_datetime,
                f1="blah",
            )
        form = CrfThreeForm(
            data=dict(
                subject_visit=subject_visit,
                report_datetime=appointments[0].appt_datetime,
                appt_date=appointments[0].appt_datetime + relativedelta(days=3),
                f1=appointments[1].visit_code,
            )
        )
        form.is_valid()
        self.assertEqual({}, form._errors)
        form.save(commit=True)

        appointments = Appointment.objects.all().order_by("timepoint", "visit_code_sequence")
        self.assertEqual(
            (appointments[0].appt_datetime + relativedelta(days=3)).date(),
            appointments[1].appt_datetime.date(),
        )

        traveller = time_machine.travel(appointments[0].appt_datetime + relativedelta(days=3))
        traveller.start()
        appointments[1].appt_status = IN_PROGRESS_APPT
        appointments[1].save()
        subject_visit = SubjectVisit.objects.create(
            appointment=appointments[1],
            report_datetime=appointments[1].appt_datetime,
            reason=SCHEDULED,
        )
        appointments = Appointment.objects.all().order_by("timepoint", "visit_code_sequence")
        for model_cls in [CrfOne, CrfTwo, CrfFour, CrfFive]:
            model_cls.objects.create(
                subject_visit=subject_visit,
                report_datetime=appointments[1].appt_datetime,
                f1="blah",
            )
        form = CrfThreeForm(
            data=dict(
                subject_visit=subject_visit,
                report_datetime=appointments[1].appt_datetime,
                appt_date=appointments[1].appt_datetime + relativedelta(days=5),
                f1=appointments[1].visit_code,
                allow_create_interim=True,
            )
        )
        form.is_valid()
        self.assertEqual({}, form._errors)
        form.save(commit=True)

        appointments = Appointment.objects.all().order_by("timepoint", "visit_code_sequence")
        self.assertEqual(appointments[2].visit_code, "1010")
        self.assertEqual(appointments[2].visit_code_sequence, 1)

        self.assertEqual(
            (appointments[1].appt_datetime + relativedelta(days=5)).date(),
            appointments[2].appt_datetime.date(),
        )

        # appointments = Appointment.objects.all().order_by("timepoint", "visit_code_sequence")
        # subject_visit = SubjectVisit.objects.get(appointment=appointments[1])
        # form = CrfThreeForm(
        #     data=dict(
        #         subject_visit=subject_visit,
        #         report_datetime=appointments[1].appt_datetime,
        #         appt_date=appointments[1].appt_datetime + relativedelta(days=7),
        #         f1=appointments[1].visit_code,
        #         allow_create_interim=True,
        #     )
        # )
        # form.is_valid()
        # self.assertEqual({}, form._errors)
        # form.save(commit=True)
