from __future__ import print_function

from django.test import TestCase
from django.utils import timezone

from edc.core.bhp_variables.models import StudySite
from edc.lab.lab_profile.classes import site_lab_profiles
from edc.lab.lab_profile.exceptions import AlreadyRegistered as AlreadyRegisteredLabProfile
from edc.subject.appointment.models import Appointment
from edc.subject.lab_tracker.classes import site_lab_tracker
from edc.subject.registration.tests.factories.registered_subject_factory import RegisteredSubjectFactory
from edc.subject.visit_schedule.models import VisitDefinition
from edc.testing.classes import TestLabProfile
from edc.testing.classes import TestVisitSchedule, TestAppConfiguration
from edc.testing.models import TestVisit
from edc.testing.tests.factories import TestConsentWithMixinFactory
from edc.testing.tests.factories import TestVisitFactory
from edc_constants.constants import MALE, SCHEDULED


class BaseTest(TestCase):

    app_label = 'testing'
    consent_catalogue_name = 'v1'

    def setUp(self):
        try:
            site_lab_profiles.register(TestLabProfile())
        except AlreadyRegisteredLabProfile:
            pass
        site_lab_tracker.autodiscover()

        TestAppConfiguration().prepare()

        TestVisitSchedule().build()

        self.test_visit_factory = TestVisitFactory
        self.study_site = StudySite.objects.all()[0]
        visit_definition = VisitDefinition.objects.get(code='1000')

        # create a subject one
        test_consent = TestConsentWithMixinFactory(
            gender=MALE,
            study_site=self.study_site,
            identity='111111111',
            confirm_identity='111111111',
            subject_identifier='999-100000-2')
        registered_subject = RegisteredSubjectFactory(
            subject_identifier=test_consent.subject_identifier)
        appointment = Appointment.objects.create(
            registered_subject=registered_subject,
            appt_datetime=timezone.now(),
            visit_definition=visit_definition)
        TestVisit.objects.create(
            appointment=appointment,
            report_datetime=timezone.now(),
            reason=SCHEDULED)

        # create a subject tow, for the tests
        self.test_consent = TestConsentWithMixinFactory(
            gender=MALE,
            study_site=self.study_site,
            identity='111111112',
            confirm_identity='111111112',
            subject_identifier='999-100000-1')
        self.registered_subject = RegisteredSubjectFactory(
            subject_identifier=self.test_consent.subject_identifier)
        self.appointment_count = VisitDefinition.objects.all().count()
