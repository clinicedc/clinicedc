from django.test import TestCase, tag
from edc_appointment.apps import EdcAppointmentAppConfigError
from edc_base.utils import get_utcnow
from edc_model_wrapper import ModelWrapper

from ..model_wrappers import AppointmentModelWrapper, SubjectVisitModelWrapper
from ..model_wrappers import AppointmentModelWrapperError
from .models import SubjectVisit, Appointment
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from .visit_schedule import visit_schedule1


class MySubjectVisitModelWrapper(SubjectVisitModelWrapper):

    model = "edc_subject_dashboard.subjectvisit"


class TestModelWrapper(TestCase):
    def setUp(self):
        site_visit_schedules._registry = {}
        site_visit_schedules.register(visit_schedule=visit_schedule1)

    @tag("1")
    def test_(self):
        """Assert determines appointment model from model_obj.
        """
        model_obj = Appointment(visit_schedule_name="visit_schedule1")
        wrapper = AppointmentModelWrapper(model_obj=model_obj)
        self.assertEqual(wrapper.model, "edc_appointment.appointment")
        self.assertEqual(wrapper.model_cls, Appointment)

    @tag("1")
    def test_with_visit_model_wrapper_cls_bad(self):
        """Assert determines appointment model from
        visit model wrapper.
        """

        class MyAppointmentModelWrapper(AppointmentModelWrapper):
            visit_model_wrapper_cls = ModelWrapper

        model_obj = Appointment(visit_schedule_name="visit_schedule1")
        self.assertRaises(
            EdcAppointmentAppConfigError, MyAppointmentModelWrapper, model_obj=model_obj
        )

    @tag("1")
    def test_with_visit_model_wrapper_cls_bad2(self):
        """Assert raises if subject visit model is not
        in the Appointment configurations.
        """

        class MyAppSubjectVisitModelWrapper(ModelWrapper):
            model = "myapp.subjectvisit"

        class MyAppointmentModelWrapper(AppointmentModelWrapper):
            visit_model_wrapper_cls = MyAppSubjectVisitModelWrapper
            model = "edc_appointment.appointment"

        model_obj = Appointment(visit_schedule_name="visit_schedule1")
        self.assertRaises(
            EdcAppointmentAppConfigError, MyAppointmentModelWrapper, model_obj=model_obj
        )

    @tag("1")
    def test_with_visit_model_wrapper_cls_bad3(self):
        """Assert raises if the model is speified and does not
        match the appointment relative to the if subject visit model
        from the Appointment configurations.
        """

        class MyAppointmentModelWrapper(AppointmentModelWrapper):
            visit_model_wrapper_cls = MySubjectVisitModelWrapper
            model = "myapp.appointment"

        model_obj = Appointment(visit_schedule_name="visit_schedule1")
        self.assertRaises(
            AppointmentModelWrapperError, MyAppointmentModelWrapper, model_obj=model_obj
        )

    @tag("1")
    def test_with_visit_model_wrapper_cls_ok(self):
        """Assert determines appointment model from
        visit model wrapper.
        """

        class MyAppointmentModelWrapper(AppointmentModelWrapper):
            visit_model_wrapper_cls = MySubjectVisitModelWrapper

        model_obj = Appointment(visit_schedule_name="visit_schedule1")
        wrapper = MyAppointmentModelWrapper(model_obj=model_obj)
        self.assertEqual(wrapper.model, "edc_appointment.appointment")
        self.assertEqual(wrapper.model_cls, Appointment)

    @tag("1")
    def test_model_wrapper_forced_rewrap(self):
        """Assert visit model wrapper can be referenced more than once.
        """

        class MyAppointmentModelWrapper(AppointmentModelWrapper):
            visit_model_wrapper_cls = MySubjectVisitModelWrapper

        subject_identifier = "12345"
        report_datetime = get_utcnow()
        appointment = Appointment(
            subject_identifier=subject_identifier, visit_schedule_name="visit_schedule1"
        )
        subject_visit = SubjectVisit(
            subject_identifier=subject_identifier,
            appointment=appointment,
            report_datetime=report_datetime,
        )
        wrapper = MyAppointmentModelWrapper(model_obj=appointment)

        self.assertEqual(wrapper.wrapped_visit.object, subject_visit)
        # call again, trigger a forced re-wrap
        self.assertEqual(wrapper.wrapped_visit.object, subject_visit)
