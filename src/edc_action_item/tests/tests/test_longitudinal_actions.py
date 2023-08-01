from django.apps import apps as django_apps
from django.test import TestCase
from edc_appointment.models import Appointment
from edc_facility import import_holidays
from edc_visit_tracking.constants import SCHEDULED

from edc_action_item import site_action_items
from edc_action_item.models import ActionItem

from ..action_items import CrfLongitudinalOneAction, CrfLongitudinalTwoAction
from ..models import CrfLongitudinalOne
from ..test_case_mixin import TestCaseMixin


class TestLongitudinal(TestCaseMixin, TestCase):
    @classmethod
    def setUpClass(cls):
        import_holidays()
        return super().setUpClass()

    def setUp(self):
        site_action_items.registry = {}
        site_action_items.register(CrfLongitudinalOneAction)
        site_action_items.register(CrfLongitudinalTwoAction)
        self.subject_identifier = self.enroll()

    def test_(self):
        appointment = Appointment.objects.get(
            subject_identifier=self.subject_identifier,
            visit_code="1000",
        )
        subject_visit = django_apps.get_model(
            "edc_visit_tracking.subjectvisit"
        ).objects.create(
            appointment=appointment,
            reason=SCHEDULED,
        )
        crf_one_a = CrfLongitudinalOne.objects.create(subject_visit=subject_visit)
        ActionItem.objects.get(action_identifier=crf_one_a.action_identifier)
        appointment = Appointment.objects.get(
            subject_identifier=self.subject_identifier,
            visit_code="2000",
        )
        subject_visit = django_apps.get_model(
            "edc_visit_tracking.subjectvisit"
        ).objects.create(
            appointment=appointment,
            reason=SCHEDULED,
        )

        crf_one_b = CrfLongitudinalOne.objects.create(subject_visit=subject_visit)
        ActionItem.objects.get(action_identifier=crf_one_b.action_identifier)
        self.assertNotEqual(crf_one_a.action_identifier, crf_one_b.action_identifier)
