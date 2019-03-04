from dateutil.relativedelta import relativedelta
from django.test import tag
from edc_action_item.models.action_item import ActionItem
from edc_utils import get_utcnow
from edc_locator.models import SubjectLocator
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from model_mommy import mommy

from ..exceptions import NotConsentedError
from ..requires_consent import RequiresConsent
from ..site_consents import SiteConsentError
from .consent_test_case import ConsentTestCase
from .dates_test_mixin import DatesTestMixin
from .visit_schedules import visit_schedule
from .models import CrfOne


class TestRequiresConsent(DatesTestMixin, ConsentTestCase):
    def setUp(self):
        super().setUp()
        self.subject_identifier = "12345"

    def test_(self):
        self.assertRaises(SiteConsentError, RequiresConsent)

    def test_consent_out_of_period(self):
        self.consent_object_factory()
        self.assertRaises(
            SiteConsentError,
            mommy.make_recipe,
            "edc_consent.subjectconsent",
            subject_identifier=self.subject_identifier,
        )

    def test_not_consented(self):
        self.consent_object_factory()
        self.assertRaises(
            NotConsentedError,
            RequiresConsent,
            model="edc_consent.testmodel",
            subject_identifier=self.subject_identifier,
            consent_model="edc_consent.subjectconsent",
            report_datetime=self.study_open_datetime,
        )

    def test_consented(self):
        self.consent_object_factory()
        mommy.make_recipe(
            "edc_consent.subjectconsent",
            subject_identifier=self.subject_identifier,
            consent_datetime=self.study_open_datetime + relativedelta(months=1),
        )
        try:
            RequiresConsent(
                model="edc_consent.testmodel",
                subject_identifier=self.subject_identifier,
                consent_model="edc_consent.subjectconsent",
                report_datetime=self.study_open_datetime,
            )
        except NotConsentedError:
            self.fail("NotConsentedError unexpectedly raised")

    @tag("1")
    def test_requires_consent(self):
        site_visit_schedules._registry = {}
        site_visit_schedules.register(visit_schedule)
        self.consent_object_factory()
        consent_obj = mommy.make_recipe(
            "edc_consent.subjectconsent",
            subject_identifier=self.subject_identifier,
            consent_datetime=self.study_open_datetime + relativedelta(months=1),
        )
        self.assertRaises(
            SiteConsentError,
            CrfOne.objects.create,
            subject_identifier="12345",
            report_datetime=get_utcnow(),
        )
        try:
            CrfOne.objects.create(
                subject_identifier="12345",
                report_datetime=self.study_open_datetime + relativedelta(months=1),
            )
        except (SiteConsentError, NotConsentedError) as e:
            self.fail(f"Exception unexpectedly raised. Got {e}")
        consent_obj.delete()
        self.assertRaises(
            NotConsentedError,
            CrfOne.objects.create,
            subject_identifier="12345",
            report_datetime=self.study_open_datetime + relativedelta(months=1),
        )
        self.assertRaises(
            NotConsentedError,
            SubjectLocator.objects.create,
            subject_identifier="12345",
            report_datetime=self.study_open_datetime - relativedelta(months=1),
        )

        # delete singleton action item
        # created for the subject locator
        ActionItem.objects.all().delete()

        try:
            SubjectLocator.objects.create(
                subject_identifier="12345",
                report_datetime=self.study_open_datetime + relativedelta(months=1),
            )
        except NotConsentedError as e:
            self.fail(f"NotConsentedError unexpectedly raised. Got {e}")
