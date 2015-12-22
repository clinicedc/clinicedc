from __future__ import print_function

from datetime import date
from dateutil.relativedelta import relativedelta

from django.test import TestCase
from django.utils import timezone

from edc.core.bhp_variables.models import StudySite
from edc.lab.lab_profile.classes import site_lab_profiles
from edc.lab.lab_profile.exceptions import AlreadyRegistered as AlreadyRegisteredLabProfile
from edc.subject.lab_tracker.classes import site_lab_tracker
from edc.subject.registration.tests.factories import RegisteredSubjectFactory
from edc.subject.visit_schedule.models import VisitDefinition
from edc.testing.classes import TestLabProfile
from edc.testing.classes import TestVisitSchedule, TestAppConfiguration
from edc.testing.tests.factories import TestConsentWithMixinFactory
from edc_appointment.models import Appointment
from edc_constants.constants import MALE
from edc_consent.tests import TestConsentModel, ConsentTypeFactory


class BaseTestCase(TestCase):

    def setUp(self):
        try:
            site_lab_profiles.register(TestLabProfile())
        except AlreadyRegisteredLabProfile:
            pass
        site_lab_tracker.autodiscover()

        TestAppConfiguration().prepare()

        TestVisitSchedule().build()

        self.study_site = StudySite.objects.all()[0]
        self.identity = '111111111'
        self.visit_definition = VisitDefinition.objects.get(code='1000')
#         self.test_consent = TestConsentWithMixinFactory(
#             gender=MALE,
#             dob=date.today() - relativedelta(years=35),
#             study_site=self.study_site,
#             identity=self.identity,
#             confirm_identity=self.identity,
#             subject_identifier='999-100000-1')
        self.registered_subject = RegisteredSubjectFactory(
            subject_identifier='999-100000-1')
        ConsentTypeFactory()
        TestConsentModel.quota.set_quota(2, date.today(), date.today())

