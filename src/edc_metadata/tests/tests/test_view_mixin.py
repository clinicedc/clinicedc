from datetime import datetime
from unittest.mock import MagicMock
from zoneinfo import ZoneInfo

import time_machine
from clinicedc_tests.consents import consent_v1
from clinicedc_tests.helper import Helper
from clinicedc_tests.models import CrfOne, CrfThree
from clinicedc_tests.visit_schedules.visit_schedule_metadata.visit_schedule import (
    get_visit_schedule,
)
from django.contrib.auth.models import User
from django.http.request import HttpRequest
from django.test import TestCase, override_settings, tag
from django.test.client import RequestFactory
from django.views.generic.base import ContextMixin, View

from edc_appointment.constants import INCOMPLETE_APPT
from edc_appointment.creators import UnscheduledAppointmentCreator
from edc_appointment.models import Appointment
from edc_consent import site_consents
from edc_facility.import_holidays import import_holidays
from edc_lab.models.panel import Panel
from edc_metadata.models import CrfMetadata, RequisitionMetadata
from edc_metadata.view_mixins import MetadataViewMixin
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED
from edc_visit_tracking.models import SubjectVisit

test_datetime = datetime(2019, 6, 11, 8, 00, tzinfo=ZoneInfo("UTC"))


class DummyCrfModelWrapper:
    def __init__(self, **kwargs):
        self.model_obj = kwargs.get("model_obj")
        self.model = kwargs.get("model")


class DummyRequisitionModelWrapper:
    def __init__(self, **kwargs):
        self.model_obj = kwargs.get("model_obj")
        self.model = kwargs.get("model")


class MyView(MetadataViewMixin, ContextMixin, View):
    crf_model_wrapper_cls = DummyCrfModelWrapper
    requisition_model_wrapper_cls = DummyRequisitionModelWrapper

    def __init__(self, appointment: Appointment = None, **kwargs):
        self._appointment = appointment
        super().__init__(**kwargs)

    @property
    def appointment(self) -> Appointment:
        return self._appointment


utc_tz = ZoneInfo("UTC")


@tag("metadata")
@override_settings(SITE_ID=10)
@time_machine.travel(datetime(2019, 8, 11, 8, 00, tzinfo=utc_tz))
class TestViewMixin(TestCase):
    @classmethod
    def setUpTestData(cls):
        import_holidays()
        return super().setUpTestData()

    def setUp(self):
        self.user = User.objects.create(username="erik")

        for name in [
            "one",
            "two",
            "three",
            "four",
            "five",
            "six",
            "seven",
            "eight",
            "nine",
        ]:
            Panel.objects.create(name=name)

        site_consents.registry = {}
        site_consents.register(consent_v1)
        site_visit_schedules._registry = {}
        site_visit_schedules.loaded = False
        visit_schedule = get_visit_schedule(consent_v1)
        site_visit_schedules.register(visit_schedule)
        self.assertEqual(CrfMetadata.objects.all().count(), 0)
        self.assertEqual(RequisitionMetadata.objects.all().count(), 0)

        helper = Helper()
        self.subject_visit = helper.enroll_to_baseline(
            visit_schedule_name=visit_schedule.name,
            schedule_name="schedule",
        )
        self.appointment = self.subject_visit.appointment
        self.subject_identifier = self.subject_visit.subject_identifier

    def test_view_mixin(self):
        request = RequestFactory().get("/?f=f&e=e&o=o&q=q")
        request.user = self.user
        view = MyView(request=request, appointment=self.appointment)
        view.subject_identifier = self.subject_identifier
        view.kwargs = {}
        view.get_context_data()

    def test_view_mixin_context_data_crfs(self):
        request = RequestFactory().get("/?f=f&e=e&o=o&q=q")
        request.user = self.user
        view = MyView(request=request, appointment=self.appointment)
        view.subject_identifier = self.subject_identifier
        view.kwargs = {}
        context_data = view.get_context_data()
        self.assertEqual(len(context_data.get("crfs")), 5)

    def test_view_mixin_context_data_crfs_exists(self):
        CrfOne.objects.create(subject_visit=self.subject_visit)
        CrfThree.objects.create(subject_visit=self.subject_visit)
        request = RequestFactory().get("/?f=f&e=e&o=o&q=q")
        request.user = self.user
        view = MyView(request=request, appointment=self.appointment)
        view.subject_identifier = self.subject_identifier
        view.kwargs = {}
        context_data = view.get_context_data()
        for metadata in context_data.get("crfs"):
            if metadata.model in ["clinicedc_tests.crfone", "clinicedc_tests.crfthree"]:
                self.assertIsNotNone(metadata.model_instance)
            else:
                self.assertIsNone(metadata.model_instance)

    def test_view_mixin_context_data_requisitions(self):
        request = RequestFactory().get("/?f=f&e=e&o=o&q=q")
        request.user = self.user
        view = MyView(request=request, appointment=self.appointment)
        view.subject_identifier = self.subject_identifier
        context_data = view.get_context_data()
        self.assertEqual(len(context_data.get("requisitions")), 2)

    def test_view_mixin_context_data_crfs_unscheduled(self):
        self.appointment.appt_status = INCOMPLETE_APPT
        self.appointment.save()
        creator = UnscheduledAppointmentCreator(
            subject_identifier=self.subject_identifier,
            visit_schedule_name=self.appointment.visit_schedule_name,
            schedule_name=self.appointment.schedule_name,
            visit_code=self.appointment.visit_code,
            suggested_visit_code_sequence=self.appointment.visit_code_sequence + 1,
            facility=self.appointment.facility,
        )

        SubjectVisit.objects.create(
            appointment=creator.appointment,
            subject_identifier=self.subject_identifier,
            reason=SCHEDULED,
        )

        request = RequestFactory().get("/?f=f&e=e&o=o&q=q")
        request.user = self.user
        view = MyView(request=request, appointment=creator.appointment)
        view.subject_identifier = self.subject_identifier
        view.kwargs = {}
        context_data = view.get_context_data()
        self.assertEqual(len(context_data.get("crfs")), 3)
        self.assertEqual(len(context_data.get("requisitions")), 4)

        request = RequestFactory().get("/?f=f&e=e&o=o&q=q")
        request.user = self.user

        view = MyView(request=request, appointment=self.appointment)
        view.subject_identifier = self.subject_identifier
        view.kwargs = {}
        view.request = HttpRequest()
        view.message_user = MagicMock(return_value=None)
        # view.message_user.assert_called_with(3, 4, 5, key='value')
        context_data = view.get_context_data()
        self.assertEqual(len(context_data.get("crfs")), 5)
        self.assertEqual(len(context_data.get("requisitions")), 2)
