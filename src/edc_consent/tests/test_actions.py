from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import User
from django.http.request import HttpRequest
from django.test import tag, TestCase, override_settings
from edc_consent import site_consents
from edc_protocol import Protocol
from edc_utils import get_utcnow
from model_bakery import baker

from ..actions import verify_consent, unverify_consent
from .models import SubjectConsent
from .consent_test_utils import consent_object_factory


@override_settings(
    EDC_PROTOCOL_STUDY_OPEN_DATETIME=get_utcnow() - relativedelta(years=5),
    EDC_PROTOCOL_STUDY_CLOSE_DATETIME=get_utcnow() + relativedelta(years=1),
)
class TestActions(TestCase):
    def setUp(self):
        super().setUp()
        site_consents.registry = {}
        self.study_open_datetime = Protocol().study_open_datetime
        self.study_close_datetime = Protocol().study_close_datetime
        consent_object_factory(
            start=self.study_open_datetime, end=self.study_close_datetime
        )
        self.request = HttpRequest()
        user = User.objects.create(username="erikvw")
        self.request.user = user
        baker.make_recipe(
            "edc_consent.subjectconsent",
            _quantity=3,
            consent_datetime=self.study_open_datetime + relativedelta(days=1),
        )

    def test_verify(self):
        for consent_obj in SubjectConsent.objects.all():
            verify_consent(request=self.request, consent_obj=consent_obj)
        for consent_obj in SubjectConsent.objects.all():
            self.assertTrue(consent_obj.is_verified)
            self.assertEqual(consent_obj.verified_by, "erikvw")
            self.assertIsNotNone(consent_obj.is_verified_datetime)

    def test_unverify(self):
        for consent_obj in SubjectConsent.objects.all():
            unverify_consent(consent_obj=consent_obj)
        for consent_obj in SubjectConsent.objects.all():
            self.assertFalse(consent_obj.is_verified)
            self.assertIsNone(consent_obj.verified_by)
            self.assertIsNone(consent_obj.is_verified_datetime)
