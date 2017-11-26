from django.test import TestCase, tag
from edc_appointment.apps import EdcAppointmentAppConfigError
from edc_model_wrapper import ModelWrapper

from ..model_wrappers import AppointmentModelWrapper, SubjectVisitModelWrapper
from ..model_wrappers import AppointmentModelWrapperError
from .models import Appointment


class MySubjectVisitModelWrapper(SubjectVisitModelWrapper):

    model = 'edc_subject_dashboard.subjectvisit'


class TestModelWrapper(TestCase):

    def test_(self):
        """Assert determines appointment model from model_obj.
        """
        model_obj = Appointment()
        wrapper = AppointmentModelWrapper(model_obj=model_obj)
        self.assertEqual(wrapper.model, 'edc_subject_dashboard.appointment')
        self.assertEqual(wrapper.model_cls, Appointment)

    def test_with_visit_model_wrapper_cls_bad(self):
        """Assert determines appointment model from
        visit model wrapper.
        """
        class MyAppointmentModelWrapper(AppointmentModelWrapper):
            visit_model_wrapper_cls = ModelWrapper
        model_obj = Appointment()
        self.assertRaises(
            EdcAppointmentAppConfigError,
            MyAppointmentModelWrapper, model_obj=model_obj)

    def test_with_visit_model_wrapper_cls_bad2(self):
        """Assert raises if subject visit model is not
        in the Appointment configurations.
        """
        class MyAppSubjectVisitModelWrapper(ModelWrapper):
            model = 'myapp.subjectvisit'

        class MyAppointmentModelWrapper(AppointmentModelWrapper):
            visit_model_wrapper_cls = MyAppSubjectVisitModelWrapper
            model = 'edc_subject_dashboard.appointment'

        model_obj = Appointment()
        self.assertRaises(
            EdcAppointmentAppConfigError,
            MyAppointmentModelWrapper, model_obj=model_obj)

    def test_with_visit_model_wrapper_cls_bad3(self):
        """Assert raises if the model is speified and does not
        match the appointment relative to the if subject visit model
        from the Appointment configurations.
        """
        class MyAppointmentModelWrapper(AppointmentModelWrapper):
            visit_model_wrapper_cls = MySubjectVisitModelWrapper
            model = 'myapp.appointment'

        model_obj = Appointment()
        self.assertRaises(
            AppointmentModelWrapperError,
            MyAppointmentModelWrapper, model_obj=model_obj)

    def test_with_visit_model_wrapper_cls_ok(self):
        """Assert determines appointment model from
        visit model wrapper.
        """
        class MyAppointmentModelWrapper(AppointmentModelWrapper):
            visit_model_wrapper_cls = MySubjectVisitModelWrapper

        model_obj = Appointment()
        wrapper = MyAppointmentModelWrapper(model_obj=model_obj)
        self.assertEqual(wrapper.model, 'edc_subject_dashboard.appointment')
        self.assertEqual(wrapper.model_cls, Appointment)
