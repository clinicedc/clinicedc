from django.apps import apps as django_apps
from django.test import TestCase, tag

from edc_appointment.models import Appointment
from edc_registration.models import RegisteredSubject
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED

from ..constants import REQUIRED
from ..models import CrfMetadata, RequisitionMetadata
from .models import Enrollment, CrfTwo, CrfThree, CrfFour
from .visit_schedule import visit_schedule
from edc_metadata.tests.models import SubjectVisit

edc_registration_app_config = django_apps.get_app_config('edc_registration')


class MetadataRulesTests(TestCase):

    def setUp(self):
        site_visit_schedules._registry = {}
        site_visit_schedules.loaded = False
        site_visit_schedules.register(visit_schedule)
        self.schedule = site_visit_schedules.get_schedule(
            visit_schedule_name='visit_schedule',
            schedule_name='schedule')
        self.subject_identifier = '1111111'
        RegisteredSubject.objects.create(
            subject_identifier=self.subject_identifier)
        self.assertEqual(CrfMetadata.objects.all().count(), 0)
        self.assertEqual(RequisitionMetadata.objects.all().count(), 0)
        Enrollment.objects.create(subject_identifier=self.subject_identifier)
        self.appointment = Appointment.objects.get(
            subject_identifier=self.subject_identifier,
            visit_code=self.schedule.visits.first.code)

    def test_rules_disabled(self):
        """Asserts rules are disabled.

        Does not set entry status to NOT_REQUIRED for for female
        forms ('crftwo', 'crfthree').
        """
        subject_visit = SubjectVisit.objects.create(
            appointment=self.appointment, reason=SCHEDULED)
        self.assertEqual(
            CrfMetadata.objects.get(
                model=CrfTwo._meta.label_lower,
                subject_identifier=subject_visit.subject_identifier,
                visit_code=self.first_visit.code).entry_status, REQUIRED)
        self.assertEqual(
            CrfMetadata.objects.get(
                model=CrfThree._meta.label_lower,
                subject_identifier=subject_visit.subject_identifier,
                visit_code=self.first_visit.code).entry_status, REQUIRED)
        self.assertEqual(
            CrfMetadata.objects.get(
                model=CrfFour._meta.label_lower,
                subject_identifier=subject_visit.subject_identifier,
                visit_code=self.first_visit.code).entry_status, REQUIRED)
        self.assertEqual(
            CrfMetadata.objects.get(
                model=CrfFive._meta.label_lower,
                subject_identifier=subject_visit.subject_identifier,
                visit_code=self.first_visit.code).entry_status, REQUIRED)
