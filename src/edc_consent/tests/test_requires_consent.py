from dateutil.relativedelta import relativedelta
from django.test import TestCase, override_settings
from edc_action_item.models.action_item import ActionItem
from edc_locator.models import SubjectLocator
from edc_protocol import Protocol
from edc_utils import get_utcnow
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from model_bakery import baker

from ..exceptions import NotConsentedError
from ..requires_consent import RequiresConsent
from ..site_consents import SiteConsentError, site_consents
from .consent_test_utils import consent_object_factory
from .models import CrfOne, SubjectVisit
from .visit_schedules import visit_schedule


@override_settings(
    EDC_PROTOCOL_STUDY_OPEN_DATETIME=get_utcnow() - relativedelta(years=5),
    EDC_PROTOCOL_STUDY_CLOSE_DATETIME=get_utcnow() + relativedelta(years=1),
)
class TestRequiresConsent(TestCase):
    def setUp(self):
        super().setUp()
        site_consents.registry = {}
        self.subject_identifier = "12345"
        self.study_open_datetime = Protocol().study_open_datetime
        self.study_close_datetime = Protocol().study_close_datetime

    def test_(self):
        self.assertRaises(SiteConsentError, RequiresConsent)

    def test_consent_out_of_period(self):
        consent_object_factory(start=self.study_open_datetime, end=self.study_close_datetime)
        self.assertRaises(
            SiteConsentError,
            baker.make_recipe,
            "edc_consent.subjectconsent",
            subject_identifier=self.subject_identifier,
            consent_datetime=self.study_close_datetime + relativedelta(days=1),
        )

    def test_not_consented(self):
        consent_object_factory(start=self.study_open_datetime, end=self.study_close_datetime)
        self.assertRaises(
            NotConsentedError,
            RequiresConsent,
            model="edc_consent.testmodel",
            subject_identifier=self.subject_identifier,
            consent_model="edc_consent.subjectconsent",
            report_datetime=self.study_open_datetime,
        )

    def test_consented(self):
        consent_object_factory(start=self.study_open_datetime, end=self.study_close_datetime)
        baker.make_recipe(
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

    def test_requires_consent(self):
        site_visit_schedules._registry = {}
        site_visit_schedules.register(visit_schedule)
        consent_object_factory(start=self.study_open_datetime, end=self.study_close_datetime)
        consent_obj = baker.make_recipe(
            "edc_consent.subjectconsent",
            subject_identifier=self.subject_identifier,
            consent_datetime=self.study_open_datetime + relativedelta(months=1),
        )
        subject_visit = SubjectVisit.objects.create(subject_identifier=self.subject_identifier)
        self.assertRaises(
            SiteConsentError,
            CrfOne.objects.create,
            subject_visit=subject_visit,
            subject_identifier="12345",
            report_datetime=self.study_close_datetime + relativedelta(months=1),
        )
        subject_visit = SubjectVisit.objects.create(subject_identifier=self.subject_identifier)
        try:
            CrfOne.objects.create(
                subject_visit=subject_visit,
                subject_identifier="12345",
                report_datetime=self.study_open_datetime + relativedelta(months=1),
            )
        except (SiteConsentError, NotConsentedError) as e:
            self.fail(f"Exception unexpectedly raised. Got {e}")
        consent_obj.delete()
        subject_visit = SubjectVisit.objects.create(subject_identifier=self.subject_identifier)
        self.assertRaises(
            NotConsentedError,
            CrfOne.objects.create,
            subject_visit=subject_visit,
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
