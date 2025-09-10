from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import time_machine
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.sites.models import Site
from django.test import override_settings, tag, TestCase
from faker import Faker
from model_bakery import baker

from edc_appointment.models import Appointment
from edc_consent.consent_definition_extension import ConsentDefinitionExtension
from edc_consent.exceptions import (
    ConsentDefinitionDoesNotExist,
    NotConsentedError,
)
from edc_consent.field_mixins import IdentityFieldsMixinError
from edc_consent.site_consents import site_consents
from edc_constants.constants import YES
from edc_facility.import_holidays import import_holidays
from edc_protocol.research_protocol_config import ResearchProtocolConfig
from edc_sites.site import sites as site_sites
from edc_sites.utils import add_or_update_django_sites
from edc_utils import get_utcnow
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED
from edc_visit_tracking.models import SubjectVisit
from tests.consents import consent1_v1, consent1_v2, consent1_v3
from tests.helper import Helper
from tests.models import (
    CrfEight,
    SubjectConsent,
    SubjectConsentV1Ext,
    SubjectVisitWithoutAppointment,
)
from tests.sites import all_sites
from tests.visit_schedules.visit_schedule_consent import get_visit_schedule
from ..consent_test_utils import consent_factory

fake = Faker()


@tag("consent")
@time_machine.travel(datetime(2025, 6, 11, 8, 00, tzinfo=ZoneInfo("UTC")))
@override_settings(
    EDC_AUTH_SKIP_SITE_AUTHS=True, EDC_AUTH_SKIP_AUTH_UPDATER=False, SITE_ID=10
)
class TestConsentModel(TestCase):
    @classmethod
    def setUpTestData(cls):
        import_holidays()
        site_sites._registry = {}
        site_sites.loaded = False
        site_sites.register(*all_sites)
        add_or_update_django_sites()

    def setUp(self):
        self.study_open_datetime = ResearchProtocolConfig().study_open_datetime
        self.study_close_datetime = ResearchProtocolConfig().study_close_datetime
        site_consents.registry = {}
        site_consents.register(consent1_v1)
        site_consents.register(consent1_v2, updated_by=consent1_v3)
        site_consents.register(consent1_v3)
        self.dob = self.study_open_datetime - relativedelta(years=25)

    def test_encryption(self):
        subject_consent = baker.make_recipe(
            "tests.subjectconsentv1",
            first_name="ERIK",
            consent_datetime=self.study_open_datetime,
            dob=get_utcnow() - relativedelta(years=25),
        )
        self.assertEqual(subject_consent.first_name, "ERIK")

    def test_gets_subject_identifier(self):
        """Asserts a blank subject identifier is set to the
        subject_identifier_as_pk.
        """
        consent = baker.make_recipe(
            "tests.subjectconsentv1",
            subject_identifier=None,
            consent_datetime=self.study_open_datetime,
            dob=get_utcnow() - relativedelta(years=25),
            site=Site.objects.get_current(),
        )
        self.assertIsNotNone(consent.subject_identifier)
        self.assertNotEqual(
            consent.subject_identifier, consent.subject_identifier_as_pk
        )
        consent.save()
        self.assertIsNotNone(consent.subject_identifier)
        self.assertNotEqual(
            consent.subject_identifier, consent.subject_identifier_as_pk
        )

    def test_subject_has_current_consent(self):
        subject_identifier = "123456789"
        identity = "987654321"
        baker.make_recipe(
            "tests.subjectconsentv1",
            subject_identifier=subject_identifier,
            identity=identity,
            confirm_identity=identity,
            consent_datetime=self.study_open_datetime + timedelta(days=1),
            dob=get_utcnow() - relativedelta(years=25),
        )
        subject_consent = site_consents.get_consent_or_raise(
            subject_identifier="123456789",
            report_datetime=self.study_open_datetime + timedelta(days=1),
            site_id=settings.SITE_ID,
        )
        self.assertEqual(subject_consent.version, "1.0")
        baker.make_recipe(
            "tests.subjectconsentv2",
            subject_identifier=subject_identifier,
            identity=identity,
            confirm_identity=identity,
            consent_datetime=self.study_open_datetime + timedelta(days=60),
            dob=get_utcnow() - relativedelta(years=25),
        )
        subject_consent = site_consents.get_consent_or_raise(
            subject_identifier="123456789",
            report_datetime=self.study_open_datetime + timedelta(days=60),
            site_id=settings.SITE_ID,
        )
        self.assertEqual(subject_consent.version, "2.0")

    def test_model_updates_version_according_to_cdef_used(self):
        """Asserts the consent model finds the cdef and updates
        column `version` using to the version number on the
        cdef.
        """
        subject_identifier = "123456789"
        identity = "987654321"
        consent = baker.make_recipe(
            "tests.subjectconsentv1",
            subject_identifier=subject_identifier,
            identity=identity,
            confirm_identity=identity,
            consent_datetime=self.study_open_datetime,
            dob=get_utcnow() - relativedelta(years=25),
        )
        self.assertEqual(consent.version, "1.0")
        consent = baker.make_recipe(
            "tests.subjectconsentv2",
            subject_identifier=subject_identifier,
            identity=identity,
            confirm_identity=identity,
            consent_datetime=self.study_open_datetime + timedelta(days=51),
            dob=get_utcnow() - relativedelta(years=25),
        )
        self.assertEqual(consent.version, "2.0")
        consent = baker.make_recipe(
            "tests.subjectconsentv3",
            subject_identifier=subject_identifier,
            identity=identity,
            confirm_identity=identity,
            consent_datetime=self.study_open_datetime + timedelta(days=101),
            dob=get_utcnow() - relativedelta(years=25),
        )
        self.assertEqual(consent.version, "3.0")

    def test_model_updates_version_according_to_cdef_used2(self):
        """Asserts the consent model finds the `cdef` and updates
        column `version` using to the version number on the
        `cdef`.

        Note: we get the `model_cls` by looking up the `cdef` first.
        """
        traveller = time_machine.travel(self.study_open_datetime)
        traveller.start()
        subject_identifier = "123456789"
        identity = "987654321"
        cdef = site_consents.get_consent_definition(
            report_datetime=self.study_open_datetime
        )
        subject_consent = baker.make_recipe(
            cdef.model,
            subject_identifier=subject_identifier,
            identity=identity,
            confirm_identity=identity,
            consent_datetime=get_utcnow(),
            dob=get_utcnow() - relativedelta(years=25),
        )
        self.assertEqual(subject_consent.version, "1.0")
        cdef = site_consents.get_consent_definition(report_datetime=get_utcnow())
        traveller.stop()

        traveller = time_machine.travel(self.study_open_datetime + timedelta(days=102))
        traveller.start()
        self.assertRaises(
            ConsentDefinitionDoesNotExist,
            baker.make_recipe,
            cdef.model,
            subject_identifier=subject_consent.subject_identifier,
            identity=identity,
            confirm_identity=identity,
            consent_datetime=get_utcnow(),
            dob=get_utcnow() - relativedelta(years=25),
        )

        cdef = site_consents.get_consent_definition(report_datetime=get_utcnow())
        consent = baker.make_recipe(
            cdef.model,
            subject_identifier=subject_identifier,
            identity=identity,
            confirm_identity=identity,
            consent_datetime=self.study_open_datetime + timedelta(days=101),
            dob=get_utcnow() - relativedelta(years=25),
        )
        self.assertEqual(consent.version, "3.0")
        traveller.stop()

    def test_model_correctly_gets_v3_by_date(self):
        """Asserts that a consent model instance created when the
        current date is within the V3 validity period correctly
        has `instance.version == 3.0`.
        """
        traveller = time_machine.travel(self.study_open_datetime + timedelta(days=110))
        traveller.start()
        subject_identifier = "123456789"
        identity = "987654321"
        consent = baker.make_recipe(
            "tests.subjectconsentv3",
            subject_identifier=subject_identifier,
            identity=identity,
            confirm_identity=identity,
            consent_datetime=get_utcnow(),
            dob=get_utcnow() - relativedelta(years=25),
        )
        self.assertEqual(consent.version, "3.0")

    def test_model_updates_from_v1_to_v2(self):
        """Assert, for a single participant, a second consent model
        instance submitted within the v2 validity period has
        version == 2.0.

        Also note that there are now 2 instances of the consent
        model for this participant.
        """
        subject_identifier = "123456789"
        identity = "987654321"

        # travel to V1 validity period
        traveller = time_machine.travel(self.study_open_datetime)
        traveller.start()
        cdef = site_consents.get_consent_definition(report_datetime=get_utcnow())
        subject_consent = baker.make_recipe(
            cdef.model,
            subject_identifier=subject_identifier,
            identity=identity,
            confirm_identity=identity,
            consent_datetime=get_utcnow(),
            dob=get_utcnow() - relativedelta(years=25),
        )
        self.assertEqual(subject_consent.version, "1.0")
        self.assertEqual(subject_consent.subject_identifier, subject_identifier)
        self.assertEqual(subject_consent.identity, identity)
        self.assertEqual(subject_consent.confirm_identity, identity)
        self.assertEqual(subject_consent.version, cdef.version)
        self.assertEqual(subject_consent.consent_definition_name, cdef.name)
        traveller.stop()

        # travel to V2 validity period
        # create second consent for the same individual
        traveller = time_machine.travel(self.study_open_datetime + timedelta(days=51))
        traveller.start()
        cdef = site_consents.get_consent_definition(report_datetime=get_utcnow())
        subject_consent = cdef.model_cls(
            subject_identifier=subject_identifier,
            identity=identity,
            confirm_identity=identity,
            consent_datetime=get_utcnow(),
            dob=get_utcnow() - relativedelta(years=25),
        )
        subject_consent.save()
        subject_consent.refresh_from_db()
        self.assertEqual(subject_consent.version, "2.0")
        self.assertEqual(subject_consent.subject_identifier, subject_identifier)
        self.assertEqual(subject_consent.identity, identity)
        self.assertEqual(subject_consent.confirm_identity, identity)
        self.assertEqual(subject_consent.consent_definition_name, cdef.name)

        self.assertEqual(SubjectConsent.objects.filter(identity=identity).count(), 2)

    def test_first_consent_is_v2(self):
        traveller = time_machine.travel(self.study_open_datetime + timedelta(days=51))
        traveller.start()
        subject_identifier = "123456789"
        identity = "987654321"

        cdef = site_consents.get_consent_definition(report_datetime=get_utcnow())
        self.assertEqual(cdef.version, "2.0")
        subject_consent = baker.make_recipe(
            cdef.model,
            subject_identifier=subject_identifier,
            identity=identity,
            confirm_identity=identity,
            consent_datetime=get_utcnow(),
            dob=get_utcnow() - relativedelta(years=25),
        )
        self.assertEqual(subject_consent.subject_identifier, subject_identifier)
        self.assertEqual(subject_consent.identity, identity)
        self.assertEqual(subject_consent.confirm_identity, identity)
        self.assertEqual(subject_consent.version, cdef.version)
        self.assertEqual(subject_consent.consent_definition_name, cdef.name)

    def test_first_consent_is_v3(self):
        traveller = time_machine.travel(self.study_open_datetime + timedelta(days=101))
        traveller.start()
        subject_identifier = "123456789"
        identity = "987654321"

        cdef = site_consents.get_consent_definition(report_datetime=get_utcnow())
        self.assertEqual(cdef.version, "3.0")
        subject_consent = baker.make_recipe(
            cdef.model,
            subject_identifier=subject_identifier,
            identity=identity,
            confirm_identity=identity,
            consent_datetime=get_utcnow(),
            dob=get_utcnow() - relativedelta(years=25),
        )
        self.assertEqual(subject_consent.subject_identifier, subject_identifier)
        self.assertEqual(subject_consent.identity, identity)
        self.assertEqual(subject_consent.confirm_identity, identity)
        self.assertEqual(subject_consent.version, cdef.version)
        self.assertEqual(subject_consent.consent_definition_name, cdef.name)

    def test_raise_with_date_past_any_consent_period(self):
        traveller = time_machine.travel(self.study_open_datetime + timedelta(days=210))
        traveller.start()
        subject_identifier = "123456789"
        identity = "987654321"
        self.assertRaises(
            ConsentDefinitionDoesNotExist,
            site_consents.get_consent_definition,
            report_datetime=get_utcnow(),
        )
        self.assertRaises(
            ConsentDefinitionDoesNotExist,
            baker.make_recipe,
            "tests.subjectconsentv1",
            subject_identifier=subject_identifier,
            identity=identity,
            confirm_identity=identity,
            consent_datetime=get_utcnow(),
            dob=get_utcnow() - relativedelta(years=25),
        )

    def test_saving_with_date_past_any_consent_period_without_consent_raises(self):

        datetime_within_consent_v1 = self.study_open_datetime + timedelta(days=10)
        cdef_v1 = site_consents.get_consent_definition(
            report_datetime=datetime_within_consent_v1
        )
        datetime_within_consent_v2 = self.study_open_datetime + timedelta(days=60)
        cdef_v2 = site_consents.get_consent_definition(
            report_datetime=datetime_within_consent_v2
        )
        datetime_within_consent_v3 = self.study_open_datetime + timedelta(days=110)
        cdef_v3 = site_consents.get_consent_definition(
            report_datetime=datetime_within_consent_v3
        )

        visit_schedule = get_visit_schedule([cdef_v1, cdef_v2, cdef_v3], extend=True)
        schedule = visit_schedule.schedules.get("schedule1")
        site_visit_schedules._registry = {}
        site_visit_schedules.register(visit_schedule)

        # jump to and test timepoint within consent v1 window
        traveller = time_machine.travel(datetime_within_consent_v1)
        traveller.start()

        # consent and add subject_visit, crf
        helper = Helper()
        subject_consent = helper.consent_and_put_on_schedule(
            visit_schedule_name=visit_schedule.name,
            schedule_name=schedule.name,
            consent_definition=cdef_v1,
        )
        self.assertEqual(subject_consent.consent_definition_name, cdef_v1.name)
        self.assertEqual(subject_consent.version, "1.0")
        self.assertEqual(cdef_v1.model, "tests.subjectconsentv1")

        try:
            subject_visit = SubjectVisit.objects.create(
                appointment=Appointment.objects.all().order_by("appt_datetime")[0],
                report_datetime=get_utcnow(),
                subject_identifier=subject_consent.subject_identifier,
                visit_schedule_name=visit_schedule.name,
                schedule_name=schedule.name,
                reason=SCHEDULED,
            )
            subject_visit.save()
            crf_one = CrfEight.objects.create(
                subject_visit=subject_visit,
                report_datetime=get_utcnow(),
            )
            crf_one.save()
        except NotConsentedError:
            self.fail("NotConsentedError unexpectedly raised")
        traveller.stop()

        # jump to and test timepoint within consent v2 window
        traveller = time_machine.travel(datetime_within_consent_v2)
        traveller.start()

        # try subject visit before consenting (v2)
        self.assertRaises(
            NotConsentedError,
            SubjectVisit.objects.create,
            appointment=Appointment.objects.all().order_by("appt_datetime")[1],
            report_datetime=get_utcnow(),
            subject_identifier=subject_consent.subject_identifier,
            visit_schedule_name=visit_schedule.name,
            schedule_name=schedule.name,
        )

        # consent (v2) and try again
        subject_consent = baker.make_recipe(
            cdef_v2.model,
            subject_identifier=subject_consent.subject_identifier,
            identity=subject_consent.identity,
            confirm_identity=subject_consent.identity,
            consent_datetime=get_utcnow(),
            dob=subject_consent.dob,
        )
        self.assertEqual(subject_consent.consent_definition_name, cdef_v2.name)
        self.assertEqual(subject_consent.version, "2.0")
        self.assertEqual(cdef_v2.model, "tests.subjectconsentv2")

        try:
            subject_visit = SubjectVisit.objects.create(
                appointment=Appointment.objects.all().order_by("appt_datetime")[1],
                report_datetime=get_utcnow(),
                subject_identifier=subject_consent.subject_identifier,
                visit_schedule_name=visit_schedule.name,
                schedule_name=schedule.name,
                reason=SCHEDULED,
            )
            subject_visit.save()
            crf_one = CrfEight.objects.create(
                subject_visit=subject_visit,
                report_datetime=get_utcnow(),
            )
            crf_one.save()
        except NotConsentedError:
            self.fail("NotConsentedError unexpectedly raised")
        traveller.stop()

        # jump to and test timepoint within consent v3 window
        traveller = time_machine.travel(datetime_within_consent_v3)
        traveller.start()

        # try subject visit before consenting (v3)
        self.assertRaises(
            NotConsentedError,
            SubjectVisit.objects.create,
            appointment=Appointment.objects.all().order_by("appt_datetime")[2],
            report_datetime=get_utcnow(),
            subject_identifier=subject_consent.subject_identifier,
            visit_schedule_name=visit_schedule.name,
            schedule_name=schedule.name,
            reason=SCHEDULED,
        )

        # consent (v3) and try again
        subject_consent = baker.make_recipe(
            cdef_v3.model,
            subject_identifier=subject_consent.subject_identifier,
            identity=subject_consent.identity,
            confirm_identity=subject_consent.identity,
            consent_datetime=get_utcnow(),
            dob=get_utcnow() - relativedelta(years=25),
        )
        self.assertEqual(subject_consent.consent_definition_name, cdef_v3.name)
        self.assertEqual(subject_consent.version, "3.0")
        self.assertEqual(cdef_v3.model, "tests.subjectconsentv3")

        try:
            subject_visit = SubjectVisit.objects.create(
                appointment=Appointment.objects.all().order_by("appt_datetime")[2],
                report_datetime=get_utcnow(),
                subject_identifier=subject_consent.subject_identifier,
                visit_schedule_name=visit_schedule.name,
                schedule_name=schedule.name,
                reason=SCHEDULED,
            )
            subject_visit.save()
            crf_one = CrfEight.objects.create(
                subject_visit=subject_visit,
                report_datetime=get_utcnow(),
            )
            crf_one.save()
        except NotConsentedError:
            self.fail("NotConsentedError unexpectedly raised")
        traveller.stop()

    def test_save_crf_with_consent_end_shortened_to_before_existing_subject_visit_raises(
        self,
    ):

        traveller = time_machine.travel(self.study_open_datetime)
        traveller.start()

        cdef_v1 = site_consents.get_consent_definition(
            report_datetime=self.study_open_datetime + timedelta(days=10)
        )
        cdef_v2 = site_consents.get_consent_definition(
            report_datetime=self.study_open_datetime + timedelta(days=60)
        )
        datetime_within_consent_v3 = self.study_open_datetime + timedelta(days=110)
        cdef_v3 = site_consents.get_consent_definition(
            report_datetime=datetime_within_consent_v3
        )

        visit_schedule = get_visit_schedule([cdef_v1, cdef_v2, cdef_v3])
        schedule = visit_schedule.schedules.get("schedule1")
        site_visit_schedules._registry = {}
        site_visit_schedules.register(visit_schedule)

        traveller.stop()
        traveller = time_machine.travel(datetime_within_consent_v3)
        traveller.start()

        # consent v3
        helper = Helper()
        subject_consent = helper.consent_and_put_on_schedule(
            visit_schedule_name=visit_schedule.name,
            schedule_name=schedule.name,
            consent_definition=cdef_v3,
        )
        self.assertEqual(subject_consent.consent_definition_name, cdef_v3.name)
        self.assertEqual(subject_consent.version, "3.0")
        self.assertEqual(cdef_v3.model, "tests.subjectconsentv3")

        # create two visits within consent v3 period
        subject_visit_1 = SubjectVisit.objects.create(
            appointment=Appointment.objects.all().order_by("appt_datetime")[0],
            report_datetime=get_utcnow(),
            subject_identifier=subject_consent.subject_identifier,
            visit_schedule_name=visit_schedule.name,
            schedule_name=schedule.name,
            reason=SCHEDULED,
        )
        subject_visit_1.save()

        # cut short v3 validity period, and introduce new v4 consent definition,
        cdef_v3.end = datetime_within_consent_v3 + relativedelta(days=1)
        cdef_v3.updated_by = "4.0"
        site_consents.registry[cdef_v3.name] = cdef_v3

        cdef_v4 = consent_factory(
            proxy_model="tests.subjectconsentv4",
            start=cdef_v3.end + relativedelta(days=1),
            end=self.study_open_datetime + timedelta(days=150),
            version="4.0",
            updates=cdef_v3,
        )

        site_consents.unregister(cdef_v3)
        site_consents.register(cdef_v3, updated_by=cdef_v4)
        site_consents.register(cdef_v4)

        visit_schedule = get_visit_schedule([cdef_v1, cdef_v2, cdef_v3, cdef_v4])
        schedule = visit_schedule.schedules.get("schedule1")
        site_visit_schedules._registry = {}
        site_visit_schedules.register(visit_schedule)

        traveller.stop()
        traveller = time_machine.travel(cdef_v3.end + relativedelta(days=20))
        traveller.start()
        cdef_v4 = site_consents.get_consent_definition(report_datetime=get_utcnow())
        self.assertEqual(cdef_v4.version, "4.0")

        # try saving CRF within already consented (v3) period
        try:
            crf_one = CrfEight.objects.create(
                subject_visit=subject_visit_1,
                report_datetime=datetime_within_consent_v3,
            )
        except NotConsentedError:
            self.fail("NotConsentedError unexpectedly raised")
        try:
            crf_one.save()
        except NotConsentedError:
            self.fail("NotConsentedError unexpectedly raised")

        # now try to save CRF at within v4 period
        crf_one.report_datetime = get_utcnow()
        self.assertRaises(NotConsentedError, crf_one.save)

        # consent v4 and try again
        subject_consent = baker.make_recipe(
            cdef_v4.model,
            subject_identifier=subject_consent.subject_identifier,
            identity=subject_consent.identity,
            confirm_identity=subject_consent.identity,
            consent_datetime=get_utcnow(),
            dob=get_utcnow() - relativedelta(years=25),
        )
        self.assertEqual(subject_consent.consent_definition_name, cdef_v4.name)
        self.assertEqual(subject_consent.version, "4.0")
        self.assertEqual(cdef_v4.model, "tests.subjectconsentv4")

        try:
            crf_one = CrfEight.objects.create(
                subject_visit=subject_visit_1,
                report_datetime=get_utcnow(),
            )
            crf_one.save()
        except NotConsentedError:
            self.fail("NotConsentedError unexpectedly raised")
        traveller.stop()

    def test_raise_with_incorrect_model_for_cdef(self):
        traveller = time_machine.travel(self.study_open_datetime + timedelta(days=120))
        traveller.start()
        subject_identifier = "123456789"
        identity = "987654321"
        cdef = site_consents.get_consent_definition(report_datetime=get_utcnow())
        self.assertEqual(cdef.model, "tests.subjectconsentv3")
        self.assertRaises(
            ConsentDefinitionDoesNotExist,
            baker.make_recipe,
            "tests.subjectconsentv1",
            subject_identifier=subject_identifier,
            identity=identity,
            confirm_identity=identity,
            consent_datetime=get_utcnow(),
            dob=get_utcnow() - relativedelta(years=25),
        )

    def test_model_str_repr_etc(self):
        obj = baker.make_recipe(
            "tests.subjectconsentv1",
            screening_identifier="ABCDEF",
            subject_identifier="12345",
            consent_datetime=self.study_open_datetime + relativedelta(days=1),
        )

        self.assertTrue(str(obj))
        self.assertTrue(repr(obj))
        self.assertTrue(obj.age_at_consent)
        self.assertTrue(obj.formatted_age_at_consent)
        self.assertEqual(obj.report_datetime, obj.consent_datetime)

    def test_checks_identity_fields_match_or_raises(self):
        self.assertRaises(
            IdentityFieldsMixinError,
            baker.make_recipe,
            "tests.subjectconsentv1",
            subject_identifier="12345",
            consent_datetime=self.study_open_datetime + relativedelta(days=1),
            identity="123456789",
            confirm_identity="987654321",
        )

    def test_version(self):
        subject_identifier = "123456789"
        identity = "987654321"

        datetime_within_consent_v1 = self.study_open_datetime + timedelta(days=10)
        cdef_v1 = site_consents.get_consent_definition(
            report_datetime=datetime_within_consent_v1
        )
        visit_schedule = get_visit_schedule([cdef_v1])
        schedule = visit_schedule.schedules.get("schedule1")
        site_visit_schedules._registry = {}
        site_visit_schedules.register(visit_schedule)

        # jump to and test timepoint within consent v1 window
        traveller = time_machine.travel(datetime_within_consent_v1)
        traveller.start()
        subject_consent = baker.make_recipe(
            cdef_v1.model,
            subject_identifier=subject_identifier,
            identity=identity,
            confirm_identity=identity,
            consent_datetime=get_utcnow(),
            dob=get_utcnow() - relativedelta(years=25),
        )
        self.assertEqual(subject_consent.consent_definition_name, cdef_v1.name)
        self.assertEqual(subject_consent.version, "1.0")

        # try subject visit before consenting
        obj = SubjectVisitWithoutAppointment.objects.create(
            report_datetime=get_utcnow(),
            subject_identifier=subject_identifier,
            visit_schedule_name=visit_schedule.name,
            schedule_name=schedule.name,
        )

        self.assertEqual(obj.consent_version, "1.0")

    def test_version_with_extension(self):
        subject_identifier = "123456789"
        identity = "987654321"

        site_consents.registry = {}

        consent_v1 = consent_factory(
            proxy_model="tests.subjectconsentv1",
            start=self.study_open_datetime,
            end=self.study_open_datetime + relativedelta(months=3),
            version="1.0",
        )
        consent_v1_ext = ConsentDefinitionExtension(
            "tests.subjectconsentv1ext",
            version="1.1",
            start=self.study_open_datetime + relativedelta(days=20),
            extends=consent_v1,
            timepoints=[1, 2],
        )

        site_consents.register(consent_v1, extended_by=consent_v1_ext)

        visit_schedule = get_visit_schedule([consent_v1], extend=True)
        schedule = visit_schedule.schedules.get("schedule1")
        site_visit_schedules._registry = {}
        site_visit_schedules.register(visit_schedule)

        traveller = time_machine.travel(
            self.study_open_datetime + relativedelta(days=10)
        )
        traveller.start()

        cdef_v1 = site_consents.get_consent_definition(report_datetime=get_utcnow())
        helper = Helper()
        subject_consent = helper.consent_and_put_on_schedule(
            visit_schedule_name=visit_schedule.name,
            schedule_name=schedule.name,
            consent_definition=cdef_v1,
        )
        # subject_consent = baker.make_recipe(
        #     cdef_v1.model,
        #     subject_identifier=subject_identifier,
        #     identity=identity,
        #     confirm_identity=identity,
        #     consent_datetime=get_utcnow(),
        #     dob=get_utcnow() - relativedelta(years=25),
        # )
        # # make appointments
        # schedule.put_on_schedule(
        #     subject_consent.subject_identifier,
        #     subject_consent.consent_datetime,
        #     skip_get_current_site=True,
        # )

        self.assertEqual(subject_consent.consent_definition_name, cdef_v1.name)
        self.assertEqual(subject_consent.version, "1.0")

        appointments = Appointment.objects.all().order_by("appt_datetime")
        self.assertEqual(appointments.count(), 3)

        subject_visit1 = SubjectVisit.objects.create(
            appointment=appointments[0],
            report_datetime=get_utcnow(),
            subject_identifier=subject_identifier,
            visit_schedule_name=visit_schedule.name,
            schedule_name=schedule.name,
            reason=SCHEDULED,
        )
        self.assertEqual(subject_visit1.consent_version, "1.0")
        traveller.stop()

        traveller = time_machine.travel(
            self.study_open_datetime + relativedelta(days=40)
        )
        traveller.start()
        SubjectConsentV1Ext.objects.create(
            subject_consent=subject_consent,
            report_datetime=get_utcnow(),
            agrees_to_extension=YES,
            site=subject_consent.site,
        )
        appointments = Appointment.objects.all().order_by("appt_datetime")
        self.assertEqual(appointments.count(), 5)

        traveller.stop()
        traveller = time_machine.travel(
            self.study_open_datetime + relativedelta(days=41)
        )
        traveller.start()

        subject_visit2 = SubjectVisit.objects.create(
            appointment=appointments[1],
            report_datetime=get_utcnow(),
            subject_identifier=subject_identifier,
            visit_schedule_name=visit_schedule.name,
            schedule_name=schedule.name,
            reason=SCHEDULED,
        )
        self.assertEqual(subject_visit2.consent_version, "1.1")

        # assert first subject visit does not change if resaved
        subject_visit1.save()
        self.assertEqual(subject_visit1.consent_version, "1.0")

        traveller.stop()
