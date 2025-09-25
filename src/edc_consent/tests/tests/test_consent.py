from datetime import datetime, timedelta
from unittest import skip
from zoneinfo import ZoneInfo

from clinicedc_tests.helper import Helper
from clinicedc_tests.models import CrfEight, SubjectVisitWithoutAppointment
from clinicedc_tests.sites import all_sites
from clinicedc_tests.visit_schedules.visit_schedule_consent.visit_schedule import (
    get_visit_schedule,
)
from dateutil.relativedelta import relativedelta
from django.test import TestCase, override_settings, tag
from model_bakery import baker

from edc_appointment.models import Appointment
from edc_consent.consent_definition import ConsentDefinition
from edc_consent.exceptions import (
    ConsentDefinitionDoesNotExist,
    ConsentDefinitionError,
    ConsentVersionSequenceError,
    NotConsentedError,
    SiteConsentError,
)
from edc_consent.site_consents import site_consents
from edc_facility.import_holidays import import_holidays
from edc_protocol.research_protocol_config import ResearchProtocolConfig
from edc_registration.models import RegisteredSubject
from edc_sites.site import sites as site_sites
from edc_sites.utils import add_or_update_django_sites
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED
from edc_visit_tracking.models import SubjectVisit

from ..consent_test_utils import consent_definition_factory


@tag("consent")
@override_settings(
    EDC_PROTOCOL_STUDY_OPEN_DATETIME=datetime.now().astimezone(tz=ZoneInfo("UTC"))
    - relativedelta(years=5),
    EDC_PROTOCOL_STUDY_CLOSE_DATETIME=datetime.now().astimezone(tz=ZoneInfo("UTC"))
    + relativedelta(years=1),
    EDC_AUTH_SKIP_SITE_AUTHS=True,
    EDC_AUTH_SKIP_AUTH_UPDATER=False,
    SITE_ID=10,
)
class TestConsent(TestCase):
    helper_cls = Helper

    @classmethod
    def setUpTestData(cls):
        import_holidays()
        site_sites._registry = {}
        site_sites.loaded = False
        site_sites.register(*all_sites)
        add_or_update_django_sites()

    def setUp(self):
        site_consents.registry = {}
        self.study_open_datetime = ResearchProtocolConfig().study_open_datetime
        self.study_close_datetime = ResearchProtocolConfig().study_close_datetime
        self.subject_identifier = "12345"

    def test_raises_error_if_no_consent(self):
        """Asserts SubjectConsent cannot create a new instance if
        no consents are defined.

        Note: site_consents.reset_registry called in setUp.
        """
        subject_identifier = self.subject_identifier
        self.assertRaises(
            SiteConsentError,
            baker.make_recipe,
            "clinicedc_tests.subjectconsentv1",
            subject_identifier=subject_identifier,
            consent_datetime=self.study_open_datetime,
        )

    def test_raises_error_if_no_consent2(self):
        """Asserts a model using the RequiresConsentMixin cannot create
        a new instance if subject not consented.
        """
        consent_definition = consent_definition_factory(
            start=self.study_open_datetime,
            end=self.study_close_datetime,
        )
        site_consents.register(consent_definition)
        visit_schedule = get_visit_schedule(consent_definition)
        schedule = visit_schedule.schedules.get("schedule1")
        site_visit_schedules._registry = {}
        site_visit_schedules.register(get_visit_schedule(consent_definition))
        RegisteredSubject.objects.create(subject_identifier=self.subject_identifier)
        self.assertRaises(
            NotConsentedError,
            SubjectVisitWithoutAppointment.objects.create,
            report_datetime=self.study_open_datetime,
            subject_identifier=self.subject_identifier,
            visit_schedule_name=visit_schedule.name,
            schedule_name=schedule.name,
        )

    def test_allows_create_if_consent(self):
        """Asserts can create a consent model instance if a valid
        consent.
        """
        cdef = consent_definition = consent_definition_factory(
            start=self.study_open_datetime,
            end=self.study_close_datetime,
        )
        site_consents.register(cdef)
        visit_schedule = get_visit_schedule(consent_definition)
        schedule = visit_schedule.schedules.get("schedule1")
        site_visit_schedules._registry = {}
        site_visit_schedules.register(get_visit_schedule(consent_definition))
        helper = Helper()
        subject_consent = helper.consent_and_put_on_schedule(
            consent_definition=cdef,
            schedule_name=schedule.name,
            visit_schedule_name=visit_schedule.name,
            report_datetime=self.study_open_datetime,
            age_in_years=25,
        )
        subject_visit = SubjectVisit.objects.create(
            appointment=Appointment.objects.filter(
                subject_identifier=subject_consent.subject_identifier
            )[0],
            report_datetime=subject_consent.consent_datetime,
            visit_schedule_name=visit_schedule.name,
            schedule_name=schedule.name,
            reason=SCHEDULED,
        )
        try:
            CrfEight.objects.create(
                subject_visit=subject_visit,
                report_datetime=self.study_open_datetime,
            )
        except NotConsentedError:
            self.fail("NotConsentedError unexpectedly raised")

    def test_cannot_create_consent_without_consent_by_datetime(self):
        cdef = consent_definition = consent_definition_factory(
            start=self.study_open_datetime + relativedelta(days=5),
            end=self.study_close_datetime,
            version="1.0",
        )
        site_consents.register(cdef)
        visit_schedule = get_visit_schedule(consent_definition)
        schedule = visit_schedule.schedules.get("schedule1")
        site_visit_schedules._registry = {}
        site_visit_schedules.register(get_visit_schedule(consent_definition))
        helper = Helper()
        self.assertRaises(
            ConsentDefinitionDoesNotExist,
            helper.consent_and_put_on_schedule,
            consent_definition=cdef,
            schedule_name=schedule.name,
            visit_schedule_name=visit_schedule.name,
            report_datetime=self.study_open_datetime,
            age_in_years=25,
        )

    def test_consent_gets_version(self):
        cdef = consent_definition = consent_definition_factory(
            start=self.study_open_datetime, end=self.study_close_datetime, version="1.0"
        )
        site_consents.register(cdef)
        visit_schedule = get_visit_schedule(consent_definition)
        schedule = visit_schedule.schedules.get("schedule1")
        site_visit_schedules._registry = {}
        site_visit_schedules.register(get_visit_schedule(consent_definition))
        helper = Helper()
        subject_consent = helper.consent_and_put_on_schedule(
            consent_definition=cdef,
            schedule_name=schedule.name,
            visit_schedule_name=visit_schedule.name,
            report_datetime=self.study_open_datetime,
            age_in_years=25,
        )
        self.assertEqual(subject_consent.version, "1.0")

    def test_model_gets_version(self):
        cdef = consent_definition = consent_definition_factory(
            start=self.study_open_datetime, end=self.study_close_datetime, version="1.0"
        )
        site_consents.register(cdef)
        visit_schedule = get_visit_schedule(consent_definition)
        schedule = visit_schedule.schedules.get("schedule1")
        site_visit_schedules._registry = {}
        site_visit_schedules.register(get_visit_schedule(consent_definition))
        helper = Helper()
        subject_consent = helper.consent_and_put_on_schedule(
            consent_definition=cdef,
            schedule_name=schedule.name,
            visit_schedule_name=visit_schedule.name,
            report_datetime=self.study_open_datetime,
            age_in_years=25,
        )
        subject_visit = SubjectVisit.objects.create(
            appointment=Appointment.objects.filter(
                subject_identifier=subject_consent.subject_identifier
            )[0],
            report_datetime=subject_consent.consent_datetime,
            visit_schedule_name=visit_schedule.name,
            schedule_name=schedule.name,
            reason=SCHEDULED,
        )
        crf = CrfEight.objects.create(
            subject_visit=subject_visit,
            report_datetime=subject_consent.consent_datetime,
        )
        self.assertEqual(crf.consent_version, "1.0")

    def test_model_consent_version_no_change(self):
        cdef = consent_definition = consent_definition_factory(
            start=self.study_open_datetime,
            end=self.study_close_datetime,
            version="1.2",
        )
        site_consents.register(cdef)
        visit_schedule = get_visit_schedule(consent_definition)
        schedule = visit_schedule.schedules.get("schedule1")
        site_visit_schedules._registry = {}
        site_visit_schedules.register(get_visit_schedule(consent_definition))
        helper = Helper()
        subject_consent = helper.consent_and_put_on_schedule(
            consent_definition=cdef,
            schedule_name=schedule.name,
            visit_schedule_name=visit_schedule.name,
            report_datetime=self.study_open_datetime,
            age_in_years=25,
        )
        subject_visit = SubjectVisit.objects.create(
            appointment=Appointment.objects.filter(
                subject_identifier=subject_consent.subject_identifier
            )[0],
            report_datetime=subject_consent.consent_datetime,
            visit_schedule_name=visit_schedule.name,
            schedule_name=schedule.name,
            reason=SCHEDULED,
        )
        crf = CrfEight.objects.create(
            subject_visit=subject_visit,
            report_datetime=self.study_open_datetime,
        )
        self.assertEqual(crf.consent_version, "1.2")
        crf.save()
        self.assertEqual(crf.consent_version, "1.2")

    def test_multiple_consents_returned(self):
        cdef10 = consent_definition_factory(
            start=self.study_open_datetime,
            end=self.study_open_datetime + timedelta(days=50),
            version="1.0",
        )
        site_consents.register(cdef10)

        cdef11 = consent_definition_factory(
            start=self.study_open_datetime + timedelta(days=51),
            end=self.study_open_datetime + timedelta(days=100),
            version="1.1",
        )
        site_consents.register(cdef11)

        consent_datetime = self.study_open_datetime + timedelta(days=10)

        self.assertRaises(
            SiteConsentError,
            baker.make_recipe,
            cdef10.model,
            subject_identifier=self.subject_identifier,
            consent_datetime=consent_datetime,
            dob=self.study_open_datetime - relativedelta(years=25),
        )

    def test_model_consent_version_changes_with_report_datetime(self):
        cdef10 = consent_definition_factory(
            start=self.study_open_datetime,
            end=self.study_open_datetime + timedelta(days=50),
            version="1.0",
        )
        cdef20 = consent_definition_factory(
            model="clinicedc_tests.subjectconsentv2",
            start=self.study_open_datetime + timedelta(days=51),
            end=self.study_open_datetime + timedelta(days=100),
            version="2.0",
        )
        site_consents.register(cdef10)
        site_consents.register(cdef20)

        consent_datetime = self.study_open_datetime + timedelta(days=10)

        visit_schedule = get_visit_schedule([cdef10, cdef20])
        schedule = visit_schedule.schedules.get("schedule1")
        site_visit_schedules._registry = {}
        site_visit_schedules.register(visit_schedule)

        helper = Helper()
        subject_consent = helper.consent_and_put_on_schedule(
            consent_definition=cdef10,
            schedule_name=schedule.name,
            visit_schedule_name=visit_schedule.name,
            report_datetime=consent_datetime,
            age_in_years=25,
        )

        self.assertEqual(subject_consent.version, "1.0")
        self.assertEqual(subject_consent.consent_datetime, consent_datetime)

        # visit_schedule = get_visit_schedule([cdef10, cdef20])
        # schedule = visit_schedule.schedules.get("schedule1")
        # site_visit_schedules._registry = {}
        # site_visit_schedules.register(visit_schedule)

        subject_visit = SubjectVisit.objects.create(
            appointment=Appointment.objects.filter(
                subject_identifier=subject_consent.subject_identifier
            )[0],
            report_datetime=consent_datetime,
            subject_identifier=self.subject_identifier,
            visit_schedule_name=visit_schedule.name,
            schedule_name=schedule.name,
            reason=SCHEDULED,
        )

        crf = CrfEight.objects.create(
            subject_visit=subject_visit,
            report_datetime=consent_datetime,
        )
        self.assertEqual(crf.consent_version, "1.0")

        consent_datetime = self.study_open_datetime + timedelta(days=60)

        baker.make_recipe(
            cdef20.model,
            subject_identifier=subject_consent.subject_identifier,
            consent_datetime=consent_datetime,
            dob=self.study_open_datetime - relativedelta(years=25),
        )
        crf.delete()
        crf.report_datetime = consent_datetime
        crf = CrfEight.objects.create(
            subject_visit=subject_visit,
            report_datetime=consent_datetime,
        )

        self.assertEqual(crf.consent_version, "2.0")

    def test_consent_periods_cannot_overlap(self):
        cdef1 = consent_definition_factory(
            start=self.study_open_datetime,
            end=self.study_open_datetime + timedelta(days=50),
            version="1.0",
        )
        site_consents.register(cdef1)
        cdef2 = consent_definition_factory(
            start=self.study_open_datetime,
            end=self.study_open_datetime + timedelta(days=50),
            version="1.1",
        )
        self.assertRaises(ConsentDefinitionError, site_consents.register, cdef2)

    def test_consent_periods_cannot_overlap2(self):
        cdef1 = consent_definition_factory(
            model="clinicedc_tests.subjectconsentv1",
            start=self.study_open_datetime,
            end=self.study_open_datetime + timedelta(days=50),
            version="1.0",
        )

        cdef2 = consent_definition_factory(
            model="clinicedc_tests.subjectconsentv2",
            start=self.study_open_datetime,
            end=self.study_open_datetime + timedelta(days=50),
            version="2.0",
            updates=cdef1,
            validate_duration_overlap_by_model=True,
        )

        site_consents.register(cdef1, updated_by=cdef2)
        site_consents.register(cdef2)

    def test_consent_periods_can_overlap_if_different_model(self):
        cdef1 = consent_definition_factory(
            model="clinicedc_tests.subjectconsentv1",
            start=self.study_open_datetime,
            end=self.study_open_datetime + timedelta(days=50),
            version="1.0",
        )

        cdef2 = consent_definition_factory(
            model="clinicedc_tests.subjectconsentv2",
            start=self.study_open_datetime,
            end=self.study_open_datetime + timedelta(days=50),
            version="1.0",
        )

        site_consents.register(cdef1)
        try:
            site_consents.register(cdef2)
        except ConsentDefinitionError:
            self.fail("ConsentPeriodOverlapError unexpectedly raised")

    def test_consent_before_open(self):
        """Asserts cannot register a consent with a start date
        before the study open date.
        """
        self.assertRaises(
            ConsentDefinitionError,
            consent_definition_factory,
            start=self.study_open_datetime - relativedelta(days=1),
            end=self.study_close_datetime + relativedelta(days=1),
            version="1.0",
        )

    def test_consent_definition_naive_datetime_start(self):
        """Asserts cannot register a consent with a start date
        before the study open date.
        """
        d = self.study_open_datetime
        dte = datetime(d.year, d.month, d.day, 0, 0, 0, 0)

        self.assertRaises(
            ConsentDefinitionError,
            consent_definition_factory,
            start=dte,
            end=self.study_close_datetime + relativedelta(days=1),
            version="1.0",
        )

    def test_consent_definition_naive_datetime_end(self):
        """Asserts cannot register a consent with a start date
        before the study open date.
        """
        d = self.study_close_datetime
        dte = datetime(d.year, d.month, d.day, 0, 0, 0, 0)
        self.assertRaises(
            ConsentDefinitionError,
            consent_definition_factory,
            start=self.study_open_datetime,
            end=dte,
            version="1.0",
        )

    @skip
    def test_consent_update_needs_previous_version(self):
        """Asserts that a consent type updates a previous consent."""
        cdef1 = consent_definition_factory(
            start=self.study_open_datetime,
            end=self.study_open_datetime + timedelta(days=50),
            version="1.0",
        )

        # specify updates version that is not registered
        self.assertRaises(
            ConsentDefinitionError,
            consent_definition_factory,
            start=self.study_open_datetime + timedelta(days=51),
            end=self.study_open_datetime + timedelta(days=100),
            version="1.1",
            updates=cdef1,
        )
        # specify updates garbage
        self.assertRaises(
            ConsentDefinitionError,
            consent_definition_factory,
            start=self.study_open_datetime + timedelta(days=51),
            end=self.study_open_datetime + timedelta(days=100),
            version="1.1",
            updates=ConsentDefinition,
        )

        # specify updates version that exists, ok
        cdef2 = consent_definition_factory(
            start=self.study_open_datetime + timedelta(days=51),
            end=self.study_open_datetime + timedelta(days=100),
            version="1.1",
            updates=cdef1,
        )
        site_consents.register(cdef1, updated_by=cdef2)
        site_consents.register(cdef2)

    @skip
    def test_consent_model_needs_previous_version(self):
        """Asserts that a consent updates a previous consent but cannot
        be entered without an existing instance for the previous
        version."""
        consent_definition_factory(
            start=self.study_open_datetime,
            end=self.study_open_datetime + timedelta(days=50),
            version="1.0",
        )
        consent_definition_factory(
            start=self.study_open_datetime + timedelta(days=51),
            end=self.study_open_datetime + timedelta(days=100),
            version="1.1",
            update_versions=["1.0"],
        )
        self.assertRaises(
            ConsentVersionSequenceError,
            baker.make_recipe,
            "clinicedc_tests.subjectconsent",
            dob=self.study_open_datetime - relativedelta(years=25),
            consent_datetime=self.study_open_datetime + timedelta(days=60),
        )

    @skip
    def test_consent_needs_previous_version2(self):
        """Asserts that a consent model updates its previous consent."""
        consent_definition_factory(
            start=self.study_open_datetime,
            end=self.study_open_datetime + timedelta(days=50),
            version="1.0",
        )
        consent_definition_factory(
            start=self.study_open_datetime + timedelta(days=51),
            end=self.study_open_datetime + timedelta(days=100),
            version="1.1",
            update_versions=["1.0"],
        )
        subject_consent = baker.make_recipe(
            "clinicedc_tests.subjectconsent",
            consent_datetime=self.study_open_datetime + timedelta(days=5),
            dob=self.study_open_datetime - relativedelta(years=25),
        )
        self.assertEqual(subject_consent.version, "1.0")
        subject_consent = baker.make_recipe(
            "clinicedc_tests.subjectconsent",
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

    @skip
    def test_consent_needs_previous_version3(self):
        """Asserts that a consent updates a previous consent raises
        if a version is skipped.
        """
        consent_definition_factory(
            start=self.study_open_datetime,
            end=self.study_open_datetime + timedelta(days=50),
            version="1.0",
        )
        consent_definition_factory(
            start=self.study_open_datetime + timedelta(days=51),
            end=self.study_open_datetime + timedelta(days=100),
            version="1.1",
            update_versions=["1.0"],
        )
        consent_definition_factory(
            start=self.study_open_datetime + timedelta(days=101),
            end=self.study_open_datetime + timedelta(days=150),
            version="1.2",
            update_versions=["1.1"],
        )
        subject_consent = baker.make_recipe(
            "clinicedc_tests.subjectconsent",
            consent_datetime=self.study_open_datetime,
            dob=self.study_open_datetime - relativedelta(years=25),
        )
        self.assertEqual(subject_consent.version, "1.0")
        # use a consent datetime within verion 1.2, skipping 1.1, raises
        self.assertRaises(
            ConsentVersionSequenceError,
            baker.make_recipe,
            "clinicedc_tests.subjectconsent",
            consent_datetime=self.study_open_datetime + timedelta(days=125),
            subject_identifier=subject_consent.subject_identifier,
            first_name=subject_consent.first_name,
            last_name=subject_consent.last_name,
            initials=subject_consent.initials,
            identity=subject_consent.identity,
            confirm_identity=subject_consent.identity,
            dob=subject_consent.dob,
        )

    @skip
    def test_consent_may_update_more_than_one_version(self):
        consent_definition_factory(
            start=self.study_open_datetime,
            end=self.study_open_datetime + timedelta(days=50),
            version="1.0",
        )
        consent_definition_factory(
            start=self.study_open_datetime + timedelta(days=51),
            end=self.study_open_datetime + timedelta(days=100),
            version="2.0",
        )
        consent_definition_factory(
            start=self.study_open_datetime + timedelta(days=101),
            end=self.study_open_datetime + timedelta(days=150),
            version="3.0",
            update_versions=["1.0", "2.0"],
        )
