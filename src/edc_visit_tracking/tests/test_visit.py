from dateutil.relativedelta import relativedelta
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase, tag
from edc_appointment.models import Appointment
from edc_facility.import_holidays import import_holidays
from edc_utils import get_utcnow
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED

from .models import SubjectVisit, CrfOneInline, OtherModel
from .models import CrfOne, BadCrfOneInline
from .helper import Helper
from .visit_schedule import visit_schedule1, visit_schedule2
from edc_appointment.creators.unscheduled_appointment_creator import (
    UnscheduledAppointmentCreator,
)
from edc_appointment.constants import INCOMPLETE_APPT


class TestVisit(TestCase):

    helper_cls = Helper

    def setUp(self):
        import_holidays()
        self.subject_identifier = "12345"
        self.helper = self.helper_cls(subject_identifier=self.subject_identifier)
        site_visit_schedules._registry = {}
        site_visit_schedules.register(visit_schedule=visit_schedule1)
        site_visit_schedules.register(visit_schedule=visit_schedule2)

    def test_methods(self):
        self.helper.consent_and_put_on_schedule()
        appointment = Appointment.objects.all().order_by(
            "timepoint", "visit_code_sequence"
        )[0]
        subject_visit = SubjectVisit.objects.create(
            appointment=appointment, reason=SCHEDULED
        )
        instance = CrfOne(subject_visit=subject_visit)

        self.assertEqual(instance.visit, subject_visit)
        self.assertEqual(instance.visit_model_attr(), "subject_visit")
        self.assertEqual(CrfOne.visit_model_attr(), "subject_visit")
        self.assertEqual(CrfOne.visit_model_cls(), SubjectVisit)

    def test_crf_visit_model_attrs(self):
        """Assert models using the CrfModelMixin can determine which
        attribute points to the visit model foreignkey.
        """
        self.assertEqual(CrfOne().visit_model_attr(), "subject_visit")
        self.assertEqual(CrfOne.objects.all().count(), 0)

    def test_crf_visit_model(self):
        """Assert models using the CrfModelMixin can determine which
        visit model is in use for the app_label.
        """
        self.assertEqual(CrfOne().visit_model_cls(), SubjectVisit)
        self.assertEqual(CrfOne.objects.all().count(), 0)

    def test_crf_inline_model_attrs(self):
        """Assert inline model can find visit instance from parent.
        """
        self.helper.consent_and_put_on_schedule()
        appointment = Appointment.objects.all().order_by(
            "timepoint", "visit_code_sequence"
        )[0]
        subject_visit = SubjectVisit.objects.create(
            appointment=appointment, reason=SCHEDULED
        )
        crf_one = CrfOne.objects.create(subject_visit=subject_visit)
        other_model = OtherModel.objects.create()
        crf_one_inline = CrfOneInline.objects.create(
            crf_one=crf_one, other_model=other_model
        )
        self.assertEqual(crf_one_inline.visit.pk, subject_visit.pk)

    def test_crf_inline_model_parent_model(self):
        """Assert inline model cannot find parent, raises exception.
        """
        self.helper.consent_and_put_on_schedule()
        appointment = Appointment.objects.all()[0]
        subject_visit = SubjectVisit.objects.create(
            appointment=appointment, reason=SCHEDULED
        )
        crf_one = CrfOne.objects.create(subject_visit=subject_visit)
        other_model = OtherModel.objects.create()
        self.assertRaises(
            ImproperlyConfigured,
            BadCrfOneInline.objects.create,
            crf_one=crf_one,
            other_model=other_model,
        )

    def test_crf_inline_model_attrs2(self):
        """Assert inline model can find visit instance from parent.
        """
        self.helper.consent_and_put_on_schedule()
        appointment = Appointment.objects.all()[0]
        subject_visit = SubjectVisit.objects.create(
            appointment=appointment, reason=SCHEDULED
        )
        crf_one = CrfOne.objects.create(subject_visit=subject_visit)
        other_model = OtherModel.objects.create()
        crf_one_inline = CrfOneInline.objects.create(
            crf_one=crf_one, other_model=other_model
        )
        self.assertIsInstance(crf_one_inline.visit, SubjectVisit)

    def test_get_previous_model_instance(self):
        """Assert model can determine the previous.
        """
        self.helper.consent_and_put_on_schedule()
        for index, appointment in enumerate(
            Appointment.objects.all().order_by("timepoint", "visit_code_sequence")
        ):
            SubjectVisit.objects.create(
                appointment=appointment,
                report_datetime=get_utcnow() - relativedelta(months=10 - index),
                reason=SCHEDULED,
            )
        subject_visits = SubjectVisit.objects.all().order_by(
            "appointment__timepoint", "appointment__visit_code_sequence"
        )
        self.assertEqual(subject_visits.count(), 4)
        subject_visit = subject_visits[0]
        self.assertIsNone(subject_visit.previous_visit)
        subject_visit = subject_visits[1]
        self.assertEqual(subject_visit.previous_visit.pk, subject_visits[0].pk)
        subject_visit = subject_visits[2]
        self.assertEqual(subject_visit.previous_visit.pk, subject_visits[1].pk)
        subject_visit = subject_visits[3]
        self.assertEqual(subject_visit.previous_visit.pk, subject_visits[2].pk)

    def test_get_previous_model_instance2(self):
        """Assert model can determine the previous even when unscheduled
        appointment are inserted.
        """
        self.helper.consent_and_put_on_schedule()
        appointments = Appointment.objects.all().order_by(
            "timepoint", "visit_code_sequence"
        )

        for index, appointment in enumerate(appointments):
            SubjectVisit.objects.create(
                appointment=appointment,
                report_datetime=get_utcnow() - relativedelta(months=10 - index),
                reason=SCHEDULED,
            )
            appointment.appt_status = INCOMPLETE_APPT
            appointment.save()

        last_appt = appointments.last()
        for i in [1, 2]:
            appointment = UnscheduledAppointmentCreator(
                subject_identifier=self.subject_identifier,
                visit_schedule_name=last_appt.visit_schedule_name,
                schedule_name=last_appt.schedule_name,
                visit_code=last_appt.visit_code,
                facility=last_appt.facility,
            ).appointment
            SubjectVisit.objects.create(
                appointment=appointment,
                report_datetime=last_appt.appt_datetime + relativedelta(days=i),
                reason=SCHEDULED,
            )
            appointment.appt_status = INCOMPLETE_APPT
            appointment.save()

        subject_visits = SubjectVisit.objects.all().order_by(
            "appointment__timepoint", "appointment__visit_code_sequence"
        )
        self.assertEqual(subject_visits.count(), 6)

        subject_visit = subject_visits[0]
        self.assertIsNone(subject_visit.previous_visit)
        subject_visit = subject_visits[1]
        self.assertEqual(subject_visit.previous_visit, subject_visits[0])
        subject_visit = subject_visits[2]
        self.assertEqual(subject_visit.previous_visit, subject_visits[1])
        subject_visit = subject_visits[3]
        self.assertEqual(subject_visit.previous_visit, subject_visits[2])
