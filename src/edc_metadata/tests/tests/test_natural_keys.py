import unittest
from datetime import datetime
from zoneinfo import ZoneInfo

from dateutil.relativedelta import relativedelta
from django.apps import apps as django_apps
from django.conf import settings
from django.test import TestCase, override_settings
from edc_appointment.models import Appointment
from edc_consent import site_consents
from edc_consent.consent_definition import ConsentDefinition
from edc_constants.constants import FEMALE, MALE
from edc_facility.import_holidays import import_holidays
from edc_registration.models import RegisteredSubject
from edc_utils import get_utcnow
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED
from edc_visit_tracking.models import SubjectVisit
from faker import Faker

from ..models import SubjectConsentV1
from ..visit_schedule import get_visit_schedule

test_datetime = datetime(2019, 6, 11, 8, 00, tzinfo=ZoneInfo("UTC"))

skip_condition = "django_collect_offline.apps.AppConfig" not in settings.INSTALLED_APPS
skip_reason = "django_collect_offline not installed"
if not skip_condition:
    from django_collect_offline.models import OutgoingTransaction
    from django_collect_offline.tests import OfflineTestHelper

    from ...offline_models import offline_models

fake = Faker()


@unittest.skip("2")
@override_settings(
    EDC_PROTOCOL_STUDY_OPEN_DATETIME=test_datetime - relativedelta(years=3),
    EDC_PROTOCOL_STUDY_CLOSE_DATETIME=test_datetime + relativedelta(years=3),
)
class TestNaturalKey(TestCase):
    exclude_models = [
        "edc_metadata.enrollment",
        "edc_metadata.disenrollment",
        "edc_metadata.subjectrequisition",
        "edc_visit_tracking.subjectvisit",
        "edc_offstudy.subjectoffstudy",
        "edc_metadata.crfone",
        "edc_metadata.crftwo",
        "edc_metadata.crfthree",
        "edc_metadata.crffour",
        "edc_metadata.crffive",
        "edc_metadata.crfmissingmanager",
    ]

    @classmethod
    def setUpTestData(cls):
        import_holidays()

    def setUp(self):
        consent_v1 = ConsentDefinition(
            "edc_metadata.subjectconsentv1",
            version="1",
            start=get_utcnow(),
            end=get_utcnow() + relativedelta(years=3),
            age_min=18,
            age_is_adult=18,
            age_max=64,
            gender=[MALE, FEMALE],
        )
        site_consents.registry = {}
        site_consents.register(consent_v1)
        site_visit_schedules._registry = {}
        site_visit_schedules.loaded = False
        site_visit_schedules.register(get_visit_schedule(consent_v1))

        # note crfs in visit schedule are all set to REQUIRED by default.
        _, self.schedule = site_visit_schedules.get_by_onschedule_model(
            "edc_metadata.onschedule"
        )

    def enroll(self, gender=None):
        subject_identifier = fake.credit_card_number()
        subject_consent = SubjectConsentV1.objects.create(
            subject_identifier=subject_identifier,
            consent_datetime=get_utcnow(),
            gender=gender,
        )
        self.registered_subject = RegisteredSubject.objects.get(
            subject_identifier=subject_identifier
        )
        self.schedule.put_on_schedule(
            subject_identifier=subject_identifier,
            onschedule_datetime=subject_consent.consent_datetime,
        )
        self.appointment = Appointment.objects.get(
            subject_identifier=subject_identifier,
            visit_code=self.schedule.visits.first.code,
        )
        subject_visit = SubjectVisit.objects.create(
            appointment=self.appointment,
            subject_identifier=subject_identifier,
            report_datetime=self.appointment.appt_datetime,
            visit_code=self.appointment.visit_code,
            visit_code_sequence=self.appointment.visit_code_sequence,
            visit_schedule_name=self.appointment.visit_schedule_name,
            schedule_name=self.appointment.schedule_name,
            reason=SCHEDULED,
        )
        return subject_visit

    @unittest.skipIf(skip_condition, skip_reason)
    def test_natural_key_attrs(self):
        offline_helper = OfflineTestHelper()
        offline_helper.offline_test_natural_key_attr(
            "edc_metadata", exclude_models=self.exclude_models
        )

    @unittest.skipIf(skip_condition, skip_reason)
    def test_get_by_natural_key_attr(self):
        offline_helper = OfflineTestHelper()
        offline_helper.offline_test_get_by_natural_key_attr(
            "edc_metadata", exclude_models=self.exclude_models
        )

    @unittest.skipIf(skip_condition, skip_reason)
    def test_offline_test_natural_keys(self):
        offline_helper = OfflineTestHelper()
        self.enroll(MALE)
        model_objs = []
        completed_model_objs = {}
        completed_model_lower = []
        for outgoing_transaction in OutgoingTransaction.objects.all():
            if outgoing_transaction.tx_name in offline_models:
                model_cls = django_apps.get_app_config("edc_metadata").get_model(
                    outgoing_transaction.tx_name.split(".")[1]
                )
                obj = model_cls.objects.get(pk=outgoing_transaction.tx_pk)
                if outgoing_transaction.tx_name in completed_model_lower:
                    continue
                model_objs.append(obj)
                completed_model_lower.append(outgoing_transaction.tx_name)
        completed_model_objs.update({"edc_metadata": model_objs})
        offline_helper.offline_test_natural_keys(completed_model_objs)
