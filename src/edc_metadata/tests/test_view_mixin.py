from django.test import TestCase, tag
from django.views.generic.base import ContextMixin
from edc_appointment.models import Appointment
from edc_appointment import UnscheduledAppointmentCreator
from edc_reference import site_reference_configs
from edc_registration.models import RegisteredSubject
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED

from ..models import CrfMetadata, RequisitionMetadata
from ..view_mixins import MetaDataViewMixin
from .models import Enrollment, SubjectVisit, CrfOne, CrfThree
from .reference_configs import register_to_site_reference_configs
from .visit_schedule import visit_schedule
from edc_appointment.constants import INCOMPLETE_APPT


class DummyCrfModelWrapper:
    def __init__(self, **kwargs):
        self.model_obj = kwargs.get('model_obj')
        self.model = kwargs.get('model')


class DummyRequisitionModelWrapper:
    def __init__(self, **kwargs):
        self.model_obj = kwargs.get('model_obj')
        self.model = kwargs.get('model')


class MyView(MetaDataViewMixin, ContextMixin):
    crf_model_wrapper_cls = DummyCrfModelWrapper
    requisition_model_wrapper_cls = DummyRequisitionModelWrapper


class TestViewMixin(TestCase):

    def setUp(self):
        register_to_site_reference_configs()

        site_visit_schedules._registry = {}
        site_visit_schedules.loaded = False
        site_visit_schedules.register(visit_schedule)
        self.schedule = site_visit_schedules.get_schedule(
            visit_schedule_name='visit_schedule',
            schedule_name='schedule')
        site_reference_configs.register_from_visit_schedule(
            site_visit_schedules, autodiscover=False)
        self.subject_identifier = '1111111'
        RegisteredSubject.objects.create(
            subject_identifier=self.subject_identifier)
        self.assertEqual(CrfMetadata.objects.all().count(), 0)
        self.assertEqual(RequisitionMetadata.objects.all().count(), 0)
        Enrollment.objects.create(
            subject_identifier=self.subject_identifier,
            facility_name='7-day-clinic')
        self.appointment = Appointment.objects.get(
            subject_identifier=self.subject_identifier,
            visit_code=self.schedule.visits.first.code)
        self.subject_visit = SubjectVisit.objects.create(
            appointment=self.appointment,
            subject_identifier=self.subject_identifier,
            reason=SCHEDULED)

    def test_view_mixin(self):
        view = MyView()
        view.appointment = self.appointment
        view.subject_identifier = self.subject_identifier
        view.kwargs = {}
        view.get_context_data()

    def test_view_mixin_context_data_crfs(self):
        view = MyView()
        view.appointment = self.appointment
        view.subject_identifier = self.subject_identifier
        view.kwargs = {}
        context_data = view.get_context_data()
        self.assertEqual(len(context_data.get('crfs')), 5)

    def test_view_mixin_context_data_crfs_exists(self):
        CrfOne.objects.create(
            subject_visit=self.subject_visit)
        CrfThree.objects.create(
            subject_visit=self.subject_visit)
        view = MyView()
        view.appointment = self.appointment
        view.subject_identifier = self.subject_identifier
        view.kwargs = {}
        context_data = view.get_context_data()
        for metadata in context_data.get('crfs'):
            if metadata.model in ['edc_metadata.crfone', 'edc_metadata.crfthree']:
                self.assertIsNotNone(metadata.object.model_obj.id)
            else:
                self.assertIsNone(metadata.object.model_obj.id)

    def test_view_mixin_context_data_requisitions(self):
        view = MyView()
        view.appointment = self.appointment
        view.subject_identifier = self.subject_identifier
        context_data = view.get_context_data()
        self.assertEqual(len(context_data.get('requisitions')), 6)

    @tag('1')
    def test_view_mixin_context_data_crfs_unscheduled(self):
        self.appointment.appt_status = INCOMPLETE_APPT
        self.appointment.save()
        creator = UnscheduledAppointmentCreator(
            subject_identifier=self.subject_identifier,
            visit_schedule_name=self.appointment.visit_schedule_name,
            schedule_name=self.appointment.schedule_name,
            visit_code=self.appointment.visit_code,
            facility=self.appointment.facility)

        SubjectVisit.objects.create(
            appointment=creator.appointment,
            subject_identifier=self.subject_identifier,
            reason=SCHEDULED)

        view = MyView()
        view.appointment = creator.appointment
        view.subject_identifier = self.subject_identifier
        view.kwargs = {}
        context_data = view.get_context_data()
        self.assertEqual(len(context_data.get('crfs')), 3)
        self.assertEqual(len(context_data.get('requisitions')), 3)

        view = MyView()
        view.appointment = self.appointment
        view.subject_identifier = self.subject_identifier
        view.kwargs = {}
        context_data = view.get_context_data()
        self.assertEqual(len(context_data.get('crfs')), 5)
        self.assertEqual(len(context_data.get('requisitions')), 6)
