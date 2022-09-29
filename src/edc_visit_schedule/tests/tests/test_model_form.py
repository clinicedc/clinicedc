from dateutil.relativedelta import relativedelta
from django.test import TestCase, override_settings
from edc_consent import site_consents
from edc_consent.consent import Consent
from edc_constants.constants import FEMALE, MALE
from edc_facility.import_holidays import import_holidays
from edc_protocol import Protocol
from edc_reference import site_reference_configs
from edc_sites.tests import SiteTestCaseMixin
from edc_utils import get_utcnow

from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from visit_schedule_app.forms import OffScheduleForm
from visit_schedule_app.models import OnSchedule, SubjectConsent
from visit_schedule_app.visit_schedule import visit_schedule


@override_settings(
    EDC_PROTOCOL_STUDY_OPEN_DATETIME=get_utcnow() - relativedelta(years=5),
    EDC_PROTOCOL_STUDY_CLOSE_DATETIME=get_utcnow() + relativedelta(years=1),
)
class TestModels(SiteTestCaseMixin, TestCase):
    @classmethod
    def setUpClass(cls):
        import_holidays()
        super().setUpClass()

    def setUp(self):
        site_visit_schedules.loaded = False
        site_visit_schedules._registry = {}
        site_visit_schedules.register(visit_schedule)
        site_reference_configs.register_from_visit_schedule(
            visit_models={"edc_appointment.appointment": "visit_schedule_app.subjectvisit"}
        )
        v1_consent = Consent(
            "visit_schedule_app.subjectconsent",
            version="1",
            start=Protocol().study_open_datetime,
            end=Protocol().study_close_datetime,
            age_min=18,
            age_is_adult=18,
            age_max=64,
            gender=[MALE, FEMALE],
        )
        self.subject_identifier = "1234"
        site_consents.registry = {}
        site_consents.register(v1_consent)

    def test_offschedule_ok(self):
        SubjectConsent.objects.create(subject_identifier=self.subject_identifier)
        onschedule = OnSchedule.objects.create(
            subject_identifier=self.subject_identifier,
        )
        data = dict(
            subject_identifier=self.subject_identifier,
            offschedule_datetime=onschedule.onschedule_datetime + relativedelta(months=1),
        )
        form = OffScheduleForm(data=data)
        form.is_valid()
