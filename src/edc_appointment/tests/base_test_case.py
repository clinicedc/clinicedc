from datetime import date

from django.test import TestCase

from edc_base.utils import edc_base_startup
from edc_consent.models.consent_type import ConsentType
from edc_consent.tests.test_models import TestConsentModel
from edc_lab.lab_profile.classes import site_lab_profiles
from edc_lab.lab_profile.exceptions import AlreadyRegistered as AlreadyRegisteredLabProfile
from edc_registration.tests.factories import RegisteredSubjectFactory
from edc_testing.classes import TestAppConfiguration
from edc_testing.classes import TestLabProfile
from edc_visit_schedule.models import VisitDefinition

from .test_visit_schedule import VisitSchedule


class BaseTestCase(TestCase):

    def setUp(self):
        edc_base_startup()
        try:
            site_lab_profiles.register(TestLabProfile())
        except AlreadyRegisteredLabProfile:
            pass

        self.configuration = TestAppConfiguration()
        self.configuration.prepare()
        consent_type = ConsentType.objects.first()
        consent_type.app_label = 'edc_testing'
        consent_type.model_name = 'testconsentwithmixin'
        consent_type.save()

        VisitSchedule().build()

        self.study_site = '40'
        self.identity = '111111111'
        self.visit_definition = VisitDefinition.objects.get(code='1000')
        self.registered_subject = RegisteredSubjectFactory(
            subject_identifier='999-100000-1')
        self.registered_subject2 = RegisteredSubjectFactory(
            subject_identifier='999-100000-2')
        TestConsentModel.quota.set_quota(2, date.today(), date.today())
