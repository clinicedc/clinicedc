from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import User
from django.http.request import HttpRequest
from django.test import tag
from model_mommy import mommy

from ..actions import verify_consent, unverify_consent
from .consent_test_case import ConsentTestCase
from .dates_test_mixin import DatesTestMixin
from .models import SubjectConsent


class TestActions(DatesTestMixin, ConsentTestCase):
    def setUp(self):
        super().setUp()
        self.consent_object_factory()
        self.request = HttpRequest()
        user = User.objects.create(username="erikvw")
        self.request.user = user
        mommy.make_recipe(
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
