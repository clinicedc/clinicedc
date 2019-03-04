from django.http.request import HttpRequest
from django.test import TestCase, tag
from django.views.generic.base import ContextMixin, View
from edc_appointment.constants import INCOMPLETE_APPT
from edc_appointment.creators import UnscheduledAppointmentCreator
from edc_appointment.models import Appointment
from edc_facility.import_holidays import import_holidays
from edc_lab.models.panel import Panel
from edc_reference import site_reference_configs
from edc_utils import get_utcnow
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED

from ..models import CrfMetadata, RequisitionMetadata
from ..view_mixins import MetaDataViewMixin
from .models import SubjectConsent, SubjectVisit, CrfOne, CrfThree
from .reference_configs import register_to_site_reference_configs
from .visit_schedule import visit_schedule
from django.test.client import RequestFactory
from django.contrib.auth.models import User


class DummyCrfModelWrapper:
    def __init__(self, **kwargs):
        self.model_obj = kwargs.get("model_obj")
        self.model = kwargs.get("model")


class DummyRequisitionModelWrapper:
    def __init__(self, **kwargs):
        self.model_obj = kwargs.get("model_obj")
        self.model = kwargs.get("model")


class MyView(MetaDataViewMixin, ContextMixin, View):
    crf_model_wrapper_cls = DummyCrfModelWrapper
    requisition_model_wrapper_cls = DummyRequisitionModelWrapper


class TestViewMixin(TestCase):
    def setUp(self):
        import_holidays()
        register_to_site_reference_configs()
        for name in ["one", "two", "three", "four", "five", "six"]:
            Panel.objects.create(name=name)

        self.user = User.objects.create(username="erik")

        site_visit_schedules._registry = {}
        site_visit_schedules.loaded = False
        site_visit_schedules.register(visit_schedule)
        site_reference_configs.register_from_visit_schedule(
            visit_models={"edc_appointment.appointment": "edc_metadata.subjectvisit"}
        )
        self.subject_identifier = "1111111"
        self.assertEqual(CrfMetadata.objects.all().count(), 0)
        self.assertEqual(RequisitionMetadata.objects.all().count(), 0)
        subject_consent = SubjectConsent.objects.create(
            subject_identifier=self.subject_identifier, consent_datetime=get_utcnow()
        )
        _, self.schedule = site_visit_schedules.get_by_onschedule_model(
            "edc_metadata.onschedule"
        )
        self.schedule.put_on_schedule(
            subject_identifier=self.subject_identifier,
            onschedule_datetime=subject_consent.consent_datetime,
        )
        self.appointment = Appointment.objects.get(
            subject_identifier=self.subject_identifier,
            visit_code=self.schedule.visits.first.code,
        )
        self.subject_visit = SubjectVisit.objects.create(
            appointment=self.appointment,
            subject_identifier=self.subject_identifier,
            reason=SCHEDULED,
        )

    def test_view_mixin(self):
        request = RequestFactory().get("/?f=f&e=e&o=o&q=q")
        request.user = self.user
        view = MyView(request=request)
        view.appointment = self.appointment
        view.subject_identifier = self.subject_identifier
        view.kwargs = {}
        view.get_context_data()

    def test_view_mixin_context_data_crfs(self):
        request = RequestFactory().get("/?f=f&e=e&o=o&q=q")
        request.user = self.user
        view = MyView(request=request)
        view.appointment = self.appointment
        view.subject_identifier = self.subject_identifier
        view.kwargs = {}
        context_data = view.get_context_data()
        self.assertEqual(len(context_data.get("crfs")), 5)

    def test_view_mixin_context_data_crfs_exists(self):
        CrfOne.objects.create(subject_visit=self.subject_visit)
        CrfThree.objects.create(subject_visit=self.subject_visit)
        request = RequestFactory().get("/?f=f&e=e&o=o&q=q")
        request.user = self.user
        view = MyView(request=request)
        view.appointment = self.appointment
        view.subject_identifier = self.subject_identifier
        view.kwargs = {}
        context_data = view.get_context_data()
        for metadata in context_data.get("crfs"):
            if metadata.model in ["edc_metadata.crfone", "edc_metadata.crfthree"]:
                self.assertIsNotNone(metadata.object.model_obj.id)
            else:
                self.assertIsNone(metadata.object.model_obj.id)

    def test_view_mixin_context_data_requisitions(self):
        request = RequestFactory().get("/?f=f&e=e&o=o&q=q")
        request.user = self.user
        view = MyView(request=request)
        view.appointment = self.appointment
        view.subject_identifier = self.subject_identifier
        context_data = view.get_context_data()
        self.assertEqual(len(context_data.get("requisitions")), 6)

    def test_view_mixin_context_data_crfs_unscheduled(self):
        self.appointment.appt_status = INCOMPLETE_APPT
        self.appointment.save()
        creator = UnscheduledAppointmentCreator(
            subject_identifier=self.subject_identifier,
            visit_schedule_name=self.appointment.visit_schedule_name,
            schedule_name=self.appointment.schedule_name,
            visit_code=self.appointment.visit_code,
            facility=self.appointment.facility,
        )

        SubjectVisit.objects.create(
            appointment=creator.appointment,
            subject_identifier=self.subject_identifier,
            reason=SCHEDULED,
        )

        request = RequestFactory().get("/?f=f&e=e&o=o&q=q")
        request.user = self.user
        view = MyView(request=request)
        view.appointment = creator.appointment
        view.subject_identifier = self.subject_identifier
        view.kwargs = {}
        context_data = view.get_context_data()
        self.assertEqual(len(context_data.get("crfs")), 3)
        self.assertEqual(len(context_data.get("requisitions")), 3)

        request = RequestFactory().get("/?f=f&e=e&o=o&q=q")
        request.user = self.user
        view = MyView(request=request)
        view.appointment = self.appointment
        view.subject_identifier = self.subject_identifier
        view.kwargs = {}
        view.request = HttpRequest()
        view.message_user = lambda x: x
        context_data = view.get_context_data()
        self.assertEqual(len(context_data.get("crfs")), 5)
        self.assertEqual(len(context_data.get("requisitions")), 6)
