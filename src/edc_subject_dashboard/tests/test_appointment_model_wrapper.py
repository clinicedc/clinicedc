from django.test import TestCase, tag
from edc_appointment.models import Appointment
from edc_appointment.apps import EdcAppointmentAppConfigError
from edc_base.utils import get_utcnow
from edc_model_wrapper import ModelWrapper

from ..model_wrappers import AppointmentModelWrapper, SubjectVisitModelWrapper
from ..model_wrappers import AppointmentModelWrapperError
from .models import SubjectVisit


class MySubjectVisitModelWrapper(SubjectVisitModelWrapper):

    model = "edc_subject_dashboard.subjectvisit"


class TestModelWrapper(TestCase):
    def test_(self):
        """Assert determines appointment model from model_obj.
        """
        model_obj = Appointment()
        wrapper = AppointmentModelWrapper(model_obj=model_obj)
        self.assertEqual(wrapper.model, "edc_appointment.appointment")
        self.assertEqual(wrapper.model_cls, Appointment)

    def test_with_visit_model_wrapper_cls_bad(self):
        """Assert determines appointment model from
        visit model wrapper.
        """

        class MyAppointmentModelWrapper(AppointmentModelWrapper):
            visit_model_wrapper_cls = ModelWrapper

        model_obj = Appointment()
        self.assertRaises(
            EdcAppointmentAppConfigError, MyAppointmentModelWrapper, model_obj=model_obj
        )

    def test_with_visit_model_wrapper_cls_bad2(self):
        """Assert raises if subject visit model is not
        in the Appointment configurations.
        """

        class MyAppSubjectVisitModelWrapper(ModelWrapper):
            model = "myapp.subjectvisit"

        class MyAppointmentModelWrapper(AppointmentModelWrapper):
            visit_model_wrapper_cls = MyAppSubjectVisitModelWrapper
            model = "edc_appointment.appointment"

        model_obj = Appointment()
        self.assertRaises(
            EdcAppointmentAppConfigError, MyAppointmentModelWrapper, model_obj=model_obj
        )

    def test_with_visit_model_wrapper_cls_bad3(self):
        """Assert raises if the model is speified and does not
        match the appointment relative to the if subject visit model
        from the Appointment configurations.
        """

        class MyAppointmentModelWrapper(AppointmentModelWrapper):
            visit_model_wrapper_cls = MySubjectVisitModelWrapper
            model = "myapp.appointment"

        model_obj = Appointment()
        self.assertRaises(
            AppointmentModelWrapperError, MyAppointmentModelWrapper, model_obj=model_obj
        )

    def test_with_visit_model_wrapper_cls_ok(self):
        """Assert determines appointment model from
        visit model wrapper.
        """

        class MyAppointmentModelWrapper(AppointmentModelWrapper):
            visit_model_wrapper_cls = MySubjectVisitModelWrapper

        model_obj = Appointment()
        wrapper = MyAppointmentModelWrapper(model_obj=model_obj)
        self.assertEqual(wrapper.model, "edc_appointment.appointment")
        self.assertEqual(wrapper.model_cls, Appointment)

    def test_model_wrapper_forced_rewrap(self):
        """Assert visit model wrapper can be referenced more than once.
        """

        class MyAppointmentModelWrapper(AppointmentModelWrapper):
            visit_model_wrapper_cls = MySubjectVisitModelWrapper

        subject_identifier = "12345"
        report_datetime = get_utcnow()
        appointment = Appointment(subject_identifier=subject_identifier)
        subject_visit = SubjectVisit(
            subject_identifier=subject_identifier,
            appointment=appointment,
            report_datetime=report_datetime,
        )
        wrapper = MyAppointmentModelWrapper(model_obj=appointment)

        self.assertEqual(wrapper.wrapped_visit.object, subject_visit)
        # call again, trigger a forced re-wrap
        self.assertEqual(wrapper.wrapped_visit.object, subject_visit)
