from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import time_machine
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.sites.models import Site
from django.test import TestCase, override_settings
from edc_protocol.research_protocol_config import ResearchProtocolConfig
from edc_utils import get_utcnow
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from faker import Faker
from model_bakery import baker

from consent_app.models import CrfOne, SubjectConsent, SubjectVisit
from consent_app.visit_schedules import get_visit_schedule
from edc_consent.field_mixins import IdentityFieldsMixinError
from edc_consent.site_consents import site_consents

from ...exceptions import (
    ConsentDefinitionDoesNotExist,
    ConsentDefinitionModelError,
    NotConsentedError,
)
from ..consent_test_utils import consent_factory

fake = Faker()


@time_machine.travel(datetime(2019, 4, 1, 8, 00, tzinfo=ZoneInfo("UTC")))
@override_settings(
    EDC_PROTOCOL_STUDY_OPEN_DATETIME=get_utcnow() - relativedelta(years=5),
    EDC_PROTOCOL_STUDY_CLOSE_DATETIME=get_utcnow() + relativedelta(years=1),
    EDC_AUTH_SKIP_SITE_AUTHS=True,
    EDC_AUTH_SKIP_AUTH_UPDATER=False,
)
class TestConsentModel(TestCase):
    def setUp(self):
        self.study_open_datetime = ResearchProtocolConfig().study_open_datetime
        self.study_close_datetime = ResearchProtocolConfig().study_close_datetime
        site_consents.registry = {}
        self.consent_v1 = consent_factory(
            proxy_model="consent_app.subjectconsentv1",
            start=self.study_open_datetime,
            end=self.study_open_datetime + timedelta(days=50),
            version="1.0",
        )
        self.consent_v2 = consent_factory(
            proxy_model="consent_app.subjectconsentv2",
            start=self.study_open_datetime + timedelta(days=51),
            end=self.study_open_datetime + timedelta(days=100),
            version="2.0",
        )

        self.consent_v3_start_date = self.study_open_datetime + timedelta(days=101)
        self.consent_v3 = consent_factory(
            proxy_model="consent_app.subjectconsentv3",
            start=self.study_open_datetime + timedelta(days=101),
            end=self.study_open_datetime + timedelta(days=150),
            version="3.0",
            updates=self.consent_v2,
        )
        site_consents.register(self.consent_v1)
        site_consents.register(self.consent_v2, updated_by=self.consent_v3)
        site_consents.register(self.consent_v3)
        self.dob = self.study_open_datetime - relativedelta(years=25)

    def test_encryption(self):
        subject_consent = baker.make_recipe(
            "consent_app.subjectconsentv1",
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
            "consent_app.subjectconsentv1",
            subject_identifier=None,
            consent_datetime=self.study_open_datetime,
            dob=get_utcnow() - relativedelta(years=25),
            site=Site.objects.get_current(),
        )
        self.assertIsNotNone(consent.subject_identifier)
        self.assertNotEqual(consent.subject_identifier, consent.subject_identifier_as_pk)
        consent.save()
        self.assertIsNotNone(consent.subject_identifier)
        self.assertNotEqual(consent.subject_identifier, consent.subject_identifier_as_pk)

    def test_subject_has_current_consent(self):
        subject_identifier = "123456789"
        identity = "987654321"
        baker.make_recipe(
            "consent_app.subjectconsentv1",
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
            "consent_app.subjectconsentv2",
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
            "consent_app.subjectconsentv1",
            subject_identifier=subject_identifier,
            identity=identity,
            confirm_identity=identity,
            consent_datetime=self.study_open_datetime,
            dob=get_utcnow() - relativedelta(years=25),
        )
        self.assertEqual(consent.version, "1.0")
        consent = baker.make_recipe(
            "consent_app.subjectconsentv2",
            subject_identifier=subject_identifier,
            identity=identity,
            confirm_identity=identity,
            consent_datetime=self.study_open_datetime + timedelta(days=51),
            dob=get_utcnow() - relativedelta(years=25),
        )
        self.assertEqual(consent.version, "2.0")
        consent = baker.make_recipe(
            "consent_app.subjectconsentv3",
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
        subject_identifier = "123456789"
        identity = "987654321"
        cdef = site_consents.get_consent_definition(report_datetime=self.study_open_datetime)
        consent = baker.make_recipe(
            cdef.model,
            subject_identifier=subject_identifier,
            identity=identity,
            confirm_identity=identity,
            consent_datetime=self.study_open_datetime,
            dob=get_utcnow() - relativedelta(years=25),
        )
        self.assertEqual(consent.version, "1.0")
        cdef = site_consents.get_consent_definition(report_datetime=self.study_open_datetime)
        self.assertRaises(
            ConsentDefinitionModelError,
            baker.make_recipe,
            cdef.model,
            subject_identifier=subject_identifier,
            identity=identity,
            confirm_identity=identity,
            consent_datetime=self.study_open_datetime + timedelta(days=101),
            dob=get_utcnow() - relativedelta(years=25),
        )

        cdef = site_consents.get_consent_definition(
            report_datetime=self.study_open_datetime + timedelta(days=101)
        )
        consent = baker.make_recipe(
            cdef.model,
            subject_identifier=subject_identifier,
            identity=identity,
            confirm_identity=identity,
            consent_datetime=self.study_open_datetime + timedelta(days=101),
            dob=get_utcnow() - relativedelta(years=25),
        )
        self.assertEqual(consent.version, "3.0")

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
            "consent_app.subjectconsentv3",
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
        traveller = time_machine.travel(self.study_open_datetime + timedelta(days=200))
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
            "consent_app.subjectconsentv1",
            subject_identifier=subject_identifier,
            identity=identity,
            confirm_identity=identity,
            consent_datetime=get_utcnow(),
            dob=get_utcnow() - relativedelta(years=25),
        )

    def test_saving_with_date_past_any_consent_period_without_consent_raises(self):
        subject_identifier = "123456789"
        identity = "987654321"

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

        visit_schedule = get_visit_schedule([cdef_v1, cdef_v2, cdef_v3])
        schedule = visit_schedule.schedules.get("schedule1")
        site_visit_schedules._registry = {}
        site_visit_schedules.register(visit_schedule)

        # jump to and test timepoint within consent v1 window
        traveller = time_machine.travel(datetime_within_consent_v1)
        traveller.start()

        # try subject visit before consenting
        self.assertRaises(
            NotConsentedError,
            SubjectVisit.objects.create,
            report_datetime=get_utcnow(),
            subject_identifier=subject_identifier,
            visit_schedule_name=visit_schedule.name,
            schedule_name=schedule.name,
        )

        # consent and try again
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
        self.assertEqual(cdef_v1.model, "consent_app.subjectconsentv1")

        try:
            subject_visit = SubjectVisit.objects.create(
                report_datetime=get_utcnow(),
                subject_identifier=subject_identifier,
                visit_schedule_name=visit_schedule.name,
                schedule_name=schedule.name,
            )
            subject_visit.save()
            crf_one = CrfOne.objects.create(
                subject_visit=subject_visit,
                subject_identifier=subject_identifier,
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
            report_datetime=get_utcnow(),
            subject_identifier=subject_identifier,
            visit_schedule_name=visit_schedule.name,
            schedule_name=schedule.name,
        )

        # consent (v2) and try again
        subject_consent = baker.make_recipe(
            cdef_v2.model,
            subject_identifier=subject_identifier,
            identity=identity,
            confirm_identity=identity,
            consent_datetime=get_utcnow(),
            dob=get_utcnow() - relativedelta(years=25),
        )
        self.assertEqual(subject_consent.consent_definition_name, cdef_v2.name)
        self.assertEqual(subject_consent.version, "2.0")
        self.assertEqual(cdef_v2.model, "consent_app.subjectconsentv2")

        try:
            subject_visit = SubjectVisit.objects.create(
                report_datetime=get_utcnow(),
                subject_identifier=subject_identifier,
                visit_schedule_name=visit_schedule.name,
                schedule_name=schedule.name,
            )
            subject_visit.save()
            crf_one = CrfOne.objects.create(
                subject_visit=subject_visit,
                subject_identifier=subject_identifier,
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
            report_datetime=get_utcnow(),
            subject_identifier=subject_identifier,
            visit_schedule_name=visit_schedule.name,
            schedule_name=schedule.name,
        )

        # consent (v3) and try again
        subject_consent = baker.make_recipe(
            cdef_v3.model,
            subject_identifier=subject_identifier,
            identity=identity,
            confirm_identity=identity,
            consent_datetime=get_utcnow(),
            dob=get_utcnow() - relativedelta(years=25),
        )
        self.assertEqual(subject_consent.consent_definition_name, cdef_v3.name)
        self.assertEqual(subject_consent.version, "3.0")
        self.assertEqual(cdef_v3.model, "consent_app.subjectconsentv3")

        try:
            subject_visit = SubjectVisit.objects.create(
                report_datetime=get_utcnow(),
                subject_identifier=subject_identifier,
                visit_schedule_name=visit_schedule.name,
                schedule_name=schedule.name,
            )
            subject_visit.save()
            crf_one = CrfOne.objects.create(
                subject_visit=subject_visit,
                subject_identifier=subject_identifier,
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
        subject_identifier = "123456789"
        identity = "987654321"

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
        subject_consent = baker.make_recipe(
            cdef_v3.model,
            subject_identifier=subject_identifier,
            identity=identity,
            confirm_identity=identity,
            consent_datetime=get_utcnow(),
            dob=get_utcnow() - relativedelta(years=25),
        )
        self.assertEqual(subject_consent.consent_definition_name, cdef_v3.name)
        self.assertEqual(subject_consent.version, "3.0")
        self.assertEqual(cdef_v3.model, "consent_app.subjectconsentv3")

        # create two visits within consent v3 period
        subject_visit_1 = SubjectVisit.objects.create(
            report_datetime=get_utcnow(),
            subject_identifier=subject_identifier,
            visit_schedule_name=visit_schedule.name,
            schedule_name=schedule.name,
        )
        subject_visit_1.save()
        # subject_visit_2 = SubjectVisit.objects.create(
        #     report_datetime=get_utcnow() + relativedelta(days=20),
        #     subject_identifier=subject_identifier,
        #     visit_schedule_name=visit_schedule.name,
        #     schedule_name=schedule.name,
        # )
        # subject_visit_2.save()

        # cut short v3 validity period, and introduce new v4 consent definition,
        updated_v3_end_datetime = datetime_within_consent_v3 + relativedelta(days=1)
        site_consents.registry[cdef_v3.name].end = updated_v3_end_datetime
        site_consents.registry[cdef_v3.name].updated_by = "4.0"
        self.assertEqual(site_consents.registry[cdef_v3.name].end, updated_v3_end_datetime)
        self.assertEqual(site_consents.registry[cdef_v3.name].end, cdef_v3.end)
        self.assertEqual(site_consents.registry[cdef_v3.name].updated_by, "4.0")
        self.assertEqual(site_consents.registry[cdef_v3.name].updated_by, cdef_v3.updated_by)

        consent_v4 = consent_factory(
            proxy_model="consent_app.subjectconsentv4",
            start=cdef_v3.end + relativedelta(days=1),
            end=self.study_open_datetime + timedelta(days=150),
            version="4.0",
            updates=self.consent_v3,
        )

        site_consents.unregister(self.consent_v3)
        site_consents.register(self.consent_v3, updated_by=consent_v4)
        site_consents.register(consent_v4)

        traveller.stop()
        traveller = time_machine.travel(cdef_v3.end + relativedelta(days=20))
        traveller.start()
        cdef_v4 = site_consents.get_consent_definition(report_datetime=get_utcnow())
        self.assertEqual(cdef_v4.version, "4.0")
        schedule.consent_definitions = [cdef_v1, cdef_v2, cdef_v3, cdef_v4]

        # try saving CRF within already consented (v3) period
        try:
            crf_one = CrfOne.objects.create(
                subject_visit=subject_visit_1,
                subject_identifier=subject_identifier,
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
            subject_identifier=subject_identifier,
            identity=identity,
            confirm_identity=identity,
            consent_datetime=get_utcnow(),
            dob=get_utcnow() - relativedelta(years=25),
        )
        self.assertEqual(subject_consent.consent_definition_name, cdef_v4.name)
        self.assertEqual(subject_consent.version, "4.0")
        self.assertEqual(cdef_v4.model, "consent_app.subjectconsentv4")

        try:
            crf_one = CrfOne.objects.create(
                subject_visit=subject_visit_1,
                subject_identifier=subject_identifier,
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
        self.assertEqual(cdef.model, "consent_app.subjectconsentv3")
        self.assertRaises(
            ConsentDefinitionModelError,
            baker.make_recipe,
            "consent_app.subjectconsentv1",
            subject_identifier=subject_identifier,
            identity=identity,
            confirm_identity=identity,
            consent_datetime=get_utcnow(),
            dob=get_utcnow() - relativedelta(years=25),
        )

    def test_model_str_repr_etc(self):
        obj = baker.make_recipe(
            "consent_app.subjectconsentv1",
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
            "consent_app.subjectconsentv1",
            subject_identifier="12345",
            consent_datetime=self.study_open_datetime + relativedelta(days=1),
            identity="123456789",
            confirm_identity="987654321",
        )
