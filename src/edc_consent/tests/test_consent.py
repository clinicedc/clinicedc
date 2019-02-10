from datetime import timedelta, datetime
from dateutil.relativedelta import relativedelta
from django.apps import apps as django_apps
from django.test import tag
from edc_registration.models import RegisteredSubject
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from model_mommy import mommy

from ..consent import NaiveDatetimeError
from ..consent_object_validator import ConsentPeriodError, ConsentVersionSequenceError
from ..consent_object_validator import ConsentPeriodOverlapError
from ..exceptions import NotConsentedError
from ..site_consents import SiteConsentError
from .consent_test_case import ConsentTestCase
from .dates_test_mixin import DatesTestMixin
from .models import CrfOne
from .visit_schedules import visit_schedule


class TestConsent(DatesTestMixin, ConsentTestCase):
    def setUp(self):
        site_visit_schedules._registry = {}
        site_visit_schedules.register(visit_schedule)
        super().setUp()

    def test_raises_error_if_no_consent(self):
        """Asserts SubjectConsent cannot create a new instance if
        no consents are defined.

        Note: site_consents.reset_registry called in setUp.
        """
        subject_identifier = "12345"
        self.assertRaises(
            SiteConsentError,
            mommy.make_recipe,
            "edc_consent.subjectconsent",
            subject_identifier=subject_identifier,
            consent_datetime=self.study_open_datetime,
        )

    def test_raises_error_if_no_consent2(self):
        """Asserts a model using the RequiresConsentMixin cannot create
        a new instance if subject not consented.
        """
        self.consent_object_factory()
        RegisteredSubject.objects.create(subject_identifier="12345")
        self.assertRaises(
            NotConsentedError,
            CrfOne.objects.create,
            subject_identifier="12345",
            report_datetime=self.study_open_datetime,
        )

    def test_allows_create_if_consent(self):
        """Asserts can create a consent model instance if a valid
        consent.
        """
        self.consent_object_factory()
        subject_identifier = "12345"
        mommy.make_recipe(
            "edc_consent.subjectconsent",
            subject_identifier=subject_identifier,
            consent_datetime=self.study_open_datetime,
            dob=self.dob,
        )
        try:
            CrfOne.objects.create(
                subject_identifier=subject_identifier,
                report_datetime=self.study_open_datetime,
            )
        except NotConsentedError:
            self.fail("NotConsentedError unexpectedly raised")

    def test_cannot_create_consent_without_consent_by_datetime(self):
        self.consent_object_factory(
            start=self.study_open_datetime + relativedelta(days=5),
            end=self.study_close_datetime,
            version="1",
        )
        self.assertRaises(
            SiteConsentError,
            mommy.make_recipe,
            "edc_consent.subjectconsent",
            dob=self.dob,
            consent_datetime=self.study_open_datetime,
        )

    def test_consent_gets_version(self):
        self.consent_object_factory(version="1.0")
        consent = mommy.make_recipe(
            "edc_consent.subjectconsent",
            consent_datetime=self.study_open_datetime,
            dob=self.dob,
        )
        self.assertEqual(consent.version, "1.0")

    def test_model_gets_version(self):
        self.consent_object_factory(version="1.0")
        subject_identifier = "12345"
        mommy.make_recipe(
            "edc_consent.subjectconsent",
            subject_identifier=subject_identifier,
            consent_datetime=self.study_open_datetime,
            dob=self.dob,
        )
        crf_one = CrfOne.objects.create(
            subject_identifier=subject_identifier,
            report_datetime=self.study_open_datetime,
        )
        self.assertEqual(crf_one.consent_version, "1.0")

    def test_model_consent_version_no_change(self):
        self.consent_object_factory(version="1.2")
        subject_identifier = "12345"
        mommy.make_recipe(
            "edc_consent.subjectconsent",
            subject_identifier=subject_identifier,
            consent_datetime=self.study_open_datetime,
            dob=self.dob,
        )
        crf_one = CrfOne.objects.create(
            subject_identifier=subject_identifier,
            report_datetime=self.study_open_datetime,
        )
        self.assertEqual(crf_one.consent_version, "1.2")
        crf_one.save()
        self.assertEqual(crf_one.consent_version, "1.2")

    def test_model_consent_version_changes_with_report_datetime(self):
        self.consent_object_factory(
            start=self.study_open_datetime,
            end=self.study_open_datetime + timedelta(days=50),
            version="1.0",
        )
        self.consent_object_factory(
            start=self.study_open_datetime + timedelta(days=51),
            end=self.study_open_datetime + timedelta(days=100),
            version="1.1",
        )
        subject_identifier = "12345"
        consent_datetime = self.study_open_datetime + timedelta(days=10)
        subject_consent = mommy.make_recipe(
            "edc_consent.subjectconsent",
            subject_identifier=subject_identifier,
            consent_datetime=consent_datetime,
            dob=self.dob,
        )
        self.assertEqual(subject_consent.version, "1.0")
        self.assertEqual(subject_consent.subject_identifier, subject_identifier)
        self.assertEqual(subject_consent.consent_datetime, consent_datetime)
        crf_one = CrfOne.objects.create(
            subject_identifier=subject_identifier, report_datetime=consent_datetime
        )
        self.assertEqual(crf_one.consent_version, "1.0")
        consent_datetime = self.study_open_datetime + timedelta(days=60)
        subject_consent = mommy.make_recipe(
            "edc_consent.subjectconsent",
            subject_identifier=subject_identifier,
            consent_datetime=consent_datetime,
            dob=self.dob,
        )
        crf_one.report_datetime = consent_datetime
        crf_one.save()
        self.assertEqual(crf_one.consent_version, "1.1")

    def test_consent_update_needs_previous_version(self):
        """Asserts that a consent type updates a previous consent."""
        self.consent_object_factory(
            start=self.study_open_datetime,
            end=self.study_open_datetime + timedelta(days=50),
            version="1.0",
        )
        # specify updates version that does not exist, raises
        self.assertRaises(
            ConsentVersionSequenceError,
            self.consent_object_factory,
            start=self.study_open_datetime + timedelta(days=51),
            end=self.study_open_datetime + timedelta(days=100),
            version="1.1",
            updates_versions="1.2",
        )
        # specify updates version that exists, ok
        self.consent_object_factory(
            start=self.study_open_datetime + timedelta(days=51),
            end=self.study_open_datetime + timedelta(days=100),
            version="1.1",
            updates_versions="1.0",
        )

    def test_consent_model_needs_previous_version(self):
        """Asserts that a consent updates a previous consent but cannot
        be entered without an existing instance for the previous
        version."""
        self.consent_object_factory(
            start=self.study_open_datetime,
            end=self.study_open_datetime + timedelta(days=50),
            version="1.0",
        )
        self.consent_object_factory(
            start=self.study_open_datetime + timedelta(days=51),
            end=self.study_open_datetime + timedelta(days=100),
            version="1.1",
            updates_versions="1.0",
        )
        self.assertRaises(
            ConsentVersionSequenceError,
            mommy.make_recipe,
            "edc_consent.subjectconsent",
            dob=self.dob,
            consent_datetime=self.study_open_datetime + timedelta(days=60),
        )

    def test_consent_needs_previous_version2(self):
        """Asserts that a consent model updates its previous consent.
        """
        self.consent_object_factory(
            start=self.study_open_datetime,
            end=self.study_open_datetime + timedelta(days=50),
            version="1.0",
        )
        self.consent_object_factory(
            start=self.study_open_datetime + timedelta(days=51),
            end=self.study_open_datetime + timedelta(days=100),
            version="1.1",
            updates_versions="1.0",
        )
        subject_consent = mommy.make_recipe(
            "edc_consent.subjectconsent",
            consent_datetime=self.study_open_datetime + timedelta(days=5),
            dob=self.dob,
        )
        self.assertEqual(subject_consent.version, "1.0")
        subject_consent = mommy.make_recipe(
            "edc_consent.subjectconsent",
            subject_identifier=subject_consent.subject_identifier,
            consent_datetime=self.study_open_datetime + timedelta(days=60),
            first_name=subject_consent.first_name,
            last_name=subject_consent.last_name,
            initials=subject_consent.initials,
            identity=subject_consent.identity,
            confirm_identity=subject_consent.identity,
            dob=subject_consent.dob,
        )
        self.assertEqual(subject_consent.version, "1.1")

    def test_consent_needs_previous_version3(self):
        """Asserts that a consent updates a previous consent raises
        if a version is skipped.
        """
        self.consent_object_factory(
            start=self.study_open_datetime,
            end=self.study_open_datetime + timedelta(days=50),
            version="1.0",
        )
        self.consent_object_factory(
            start=self.study_open_datetime + timedelta(days=51),
            end=self.study_open_datetime + timedelta(days=100),
            version="1.1",
            updates_versions="1.0",
        )
        self.consent_object_factory(
            start=self.study_open_datetime + timedelta(days=101),
            end=self.study_open_datetime + timedelta(days=150),
            version="1.2",
            updates_versions="1.1",
        )
        subject_consent = mommy.make_recipe(
            "edc_consent.subjectconsent",
            consent_datetime=self.study_open_datetime,
            dob=self.dob,
        )
        self.assertEqual(subject_consent.version, "1.0")
        # use a consent datetime within verion 1.2, skipping 1.1, raises
        self.assertRaises(
            ConsentVersionSequenceError,
            mommy.make_recipe,
            "edc_consent.subjectconsent",
            consent_datetime=self.study_open_datetime + timedelta(days=125),
            subject_identifier=subject_consent.subject_identifier,
            first_name=subject_consent.first_name,
            last_name=subject_consent.last_name,
            initials=subject_consent.initials,
            identity=subject_consent.identity,
            confirm_identity=subject_consent.identity,
            dob=subject_consent.dob,
        )

    def test_consent_periods_cannot_overlap(self):
        self.consent_object_factory(
            start=self.study_open_datetime,
            end=self.study_open_datetime + timedelta(days=50),
            version="1.0",
        )
        self.assertRaises(
            ConsentPeriodOverlapError,
            self.consent_object_factory,
            start=self.study_open_datetime + timedelta(days=25),
            end=self.study_open_datetime + timedelta(days=100),
            version="1.1",
            updates_versions="1.0",
        )

    def test_consent_periods_cannot_overlap2(self):
        self.consent_object_factory(
            model="edc_consent.subjectconsent",
            start=self.study_open_datetime,
            end=self.study_open_datetime + timedelta(days=50),
            version="1.0",
        )
        self.assertRaises(
            ConsentPeriodOverlapError,
            self.consent_object_factory,
            model="edc_consent.subjectconsent",
            start=self.study_open_datetime,
            end=self.study_open_datetime + timedelta(days=50),
            version="1.1",
        )

    def test_consent_periods_can_overlap_if_different_model(self):
        self.consent_object_factory(
            model="edc_consent.subjectconsent",
            start=self.study_open_datetime,
            end=self.study_open_datetime + timedelta(days=50),
            version="1.0",
        )
        try:
            self.consent_object_factory(
                model="edc_consent.subjectconsent2",
                start=self.study_open_datetime,
                end=self.study_open_datetime + timedelta(days=50),
                version="1.0",
            )
        except ConsentPeriodOverlapError:
            self.fail("ConsentPeriodOverlapError unexpectedly raised")

    def test_consent_before_open(self):
        """Asserts cannot register a consent with a start date
        before the study open date.
        """
        study_open_datetime = django_apps.get_app_config(
            "edc_protocol"
        ).study_open_datetime
        study_close_datetime = django_apps.get_app_config(
            "edc_protocol"
        ).study_close_datetime
        self.assertRaises(
            ConsentPeriodError,
            self.consent_object_factory,
            start=study_open_datetime - relativedelta(days=1),
            end=study_close_datetime + relativedelta(days=1),
            version="1.0",
        )

    def test_consent_may_update_more_than_one_version(self):
        self.consent_object_factory(
            start=self.study_open_datetime,
            end=self.study_open_datetime + timedelta(days=50),
            version="1.0",
        )
        self.consent_object_factory(
            start=self.study_open_datetime + timedelta(days=51),
            end=self.study_open_datetime + timedelta(days=100),
            version="2.0",
        )
        self.consent_object_factory(
            start=self.study_open_datetime + timedelta(days=101),
            end=self.study_open_datetime + timedelta(days=150),
            version="3.0",
            updates_versions="1.0, 2.0",
        )

    def test_consent_object_naive_datetime_start(self):
        """Asserts cannot register a consent with a start date
        before the study open date.
        """
        study_open_datetime = django_apps.get_app_config(
            "edc_protocol"
        ).study_open_datetime
        study_close_datetime = django_apps.get_app_config(
            "edc_protocol"
        ).study_close_datetime
        d = study_open_datetime
        dte = datetime(d.year, d.month, d.day, 0, 0, 0, 0)
        self.assertRaises(
            NaiveDatetimeError,
            self.consent_object_factory,
            start=dte,
            end=study_close_datetime + relativedelta(days=1),
            version="1.0",
        )

    def test_consent_object_naive_datetime_end(self):
        """Asserts cannot register a consent with a start date
        before the study open date.
        """
        study_open_datetime = django_apps.get_app_config(
            "edc_protocol"
        ).study_open_datetime
        study_close_datetime = django_apps.get_app_config(
            "edc_protocol"
        ).study_close_datetime
        d = study_close_datetime
        dte = datetime(d.year, d.month, d.day, 0, 0, 0, 0)
        self.assertRaises(
            NaiveDatetimeError,
            self.consent_object_factory,
            start=study_open_datetime,
            end=dte,
            version="1.0",
        )
