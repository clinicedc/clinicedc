from django.test import TestCase
from django.utils import timezone

from edc_lab.lab_profile.classes import site_lab_profiles
from edc_lab.lab_profile.exceptions import AlreadyRegistered as AlreadyRegisteredLabProfile
from edc.subject.lab_tracker.classes import site_lab_tracker
from edc_testing.classes import TestLabProfile, TestAppConfiguration
from edc_testing.tests.factories import TestConsentWithMixinFactory
from edc_appointment.models import Appointment
from edc_constants.constants import MALE, SCHEDULED
from edc_registration.tests.factories import RegisteredSubjectFactory
from edc_visit_schedule.models import VisitDefinition

from .test_models import TestVisitModel1

from .test_visit_schedule import VisitSchedule
from edc_consent.models.consent_type import ConsentType


class BaseTestCase(TestCase):

    app_label = 'edc_testing'
    consent_catalogue_name = 'v1'

    def setUp(self):
        try:
            site_lab_profiles.register(TestLabProfile())
        except AlreadyRegisteredLabProfile:
            pass
        site_lab_tracker.autodiscover()

        self.configuration = TestAppConfiguration()
        self.configuration.prepare()
        consent_type = ConsentType.objects.first()
        consent_type.app_label = 'edc_testing'
        consent_type.model_name = 'testconsentwithmixin'
        consent_type.save()

        VisitSchedule().build()
        self.study_site = '40'
        visit_definition = VisitDefinition.objects.get(code='1000')

        # create a subject one
        registered_subject = RegisteredSubjectFactory(
            subject_identifier='999-100000-2')
        TestConsentWithMixinFactory(
            registered_subject=registered_subject,
            gender=MALE,
            study_site=self.study_site,
            identity='111111111',
            confirm_identity='111111111',
            subject_identifier='999-100000-2')
        appointment = Appointment.objects.get(
            registered_subject=registered_subject,
            visit_definition=visit_definition)
        self.test_visit_model1 = TestVisitModel1.objects.create(
            appointment=appointment,
            report_datetime=timezone.now(),
            reason=SCHEDULED)

        # create a subject tow, for the tests
        self.registered_subject = RegisteredSubjectFactory(
            subject_identifier='999-100001-3')
        self.test_consent = TestConsentWithMixinFactory(
            registered_subject=self.registered_subject,
            gender=MALE,
            study_site=self.study_site,
            identity='111111112',
            confirm_identity='111111112',
            subject_identifier='999-100001-3')
        self.appointment_count = VisitDefinition.objects.all().count()
