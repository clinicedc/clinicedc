import string
from secrets import choice

from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import User
from django.http.request import HttpRequest
from django.test import TestCase, override_settings
from edc_protocol.research_protocol_config import ResearchProtocolConfig
from edc_utils import get_utcnow
from faker import Faker
from model_bakery import baker

from consent_app.models import SubjectConsentV1
from edc_consent.actions import unverify_consent, verify_consent
from edc_consent.site_consents import site_consents

from ..consent_test_utils import consent_definition_factory

fake = Faker()


@override_settings(
    EDC_PROTOCOL_STUDY_OPEN_DATETIME=get_utcnow() - relativedelta(years=5),
    EDC_PROTOCOL_STUDY_CLOSE_DATETIME=get_utcnow() + relativedelta(years=1),
    EDC_AUTH_SKIP_SITE_AUTHS=True,
    EDC_AUTH_SKIP_AUTH_UPDATER=False,
)
class TestActions(TestCase):
    def setUp(self):
        super().setUp()
        site_consents.registry = {}
        self.study_open_datetime = ResearchProtocolConfig().study_open_datetime
        self.study_close_datetime = ResearchProtocolConfig().study_close_datetime
        cdef = consent_definition_factory(
            start=self.study_open_datetime, end=self.study_close_datetime
        )
        site_consents.register(cdef)
        self.request = HttpRequest()
        user = User.objects.create(username="erikvw")
        self.request.user = user
        for _ in range(3):
            first_name = fake.first_name()
            last_name = fake.last_name()
            initials = first_name[0] + choice(string.ascii_uppercase) + last_name[0]
            baker.make_recipe(
                "consent_app.subjectconsentv1",
                consent_datetime=self.study_open_datetime + relativedelta(days=1),
                initials=initials.upper(),
            )

    def test_verify(self):
        for consent_obj in SubjectConsentV1.objects.all():
            verify_consent(request=self.request, consent_obj=consent_obj)
        for consent_obj in SubjectConsentV1.objects.all():
            self.assertTrue(consent_obj.is_verified)
            self.assertEqual(consent_obj.verified_by, "erikvw")
            self.assertIsNotNone(consent_obj.is_verified_datetime)

    def test_unverify(self):
        for consent_obj in SubjectConsentV1.objects.all():
            unverify_consent(consent_obj=consent_obj)
        for consent_obj in SubjectConsentV1.objects.all():
            self.assertFalse(consent_obj.is_verified)
            self.assertIsNone(consent_obj.verified_by)
            self.assertIsNone(consent_obj.is_verified_datetime)
