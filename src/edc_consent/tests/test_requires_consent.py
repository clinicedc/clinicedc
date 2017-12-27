from dateutil.relativedelta import relativedelta
from django.test import tag
from model_mommy import mommy

from ..exceptions import NotConsentedError
from ..requires_consent import RequiresConsent
from ..site_consents import SiteConsentError
from .consent_test_case import ConsentTestCase
from .dates_test_mixin import DatesTestMixin


class TestRequiresConsent(DatesTestMixin, ConsentTestCase):

    def setUp(self):
        super().setUp()
        self.subject_identifier = '12345'

    def test_(self):
        self.assertRaises(SiteConsentError, RequiresConsent)

    def test_consent_out_of_period(self):
        self.consent_object_factory()
        self.assertRaises(
            SiteConsentError,
            mommy.make_recipe,
            'edc_consent.subjectconsent',
            subject_identifier=self.subject_identifier)

    def test_not_consented(self):
        self.consent_object_factory()
        self.assertRaises(
            NotConsentedError,
            RequiresConsent,
            model='edc_consent.testmodel',
            subject_identifier=self.subject_identifier,
            consent_model='edc_consent.subjectconsent',
            report_datetime=self.study_open_datetime)

    def test_consented(self):
        self.consent_object_factory()
        mommy.make_recipe(
            'edc_consent.subjectconsent',
            subject_identifier=self.subject_identifier,
            consent_datetime=self.study_open_datetime + relativedelta(months=1))
        try:
            RequiresConsent(
                model='edc_consent.testmodel',
                subject_identifier=self.subject_identifier,
                consent_model='edc_consent.subjectconsent',
                report_datetime=self.study_open_datetime)
        except NotConsentedError:
            self.fail('NotConsentedError unexpectedly raised')
