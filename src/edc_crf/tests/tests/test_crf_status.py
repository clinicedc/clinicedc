from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase, override_settings
from edc_appointment.models import Appointment
from edc_consent import site_consents
from edc_constants.constants import COMPLETE, INCOMPLETE
from edc_facility import import_holidays
from edc_reference import site_reference_configs
from edc_utils import get_utcnow
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED
from edc_visit_tracking.tests.helper import Helper
from visit_schedule_app.consents import v1_consent
from visit_schedule_app.models import SubjectConsent, SubjectVisit

from edc_crf.models import CrfStatus

from ..models import Crf
from ..visit_schedule import visit_schedule


@override_settings(
    SUBJECT_CONSENT_MODEL="visit_schedule_app.subjectconsent",
    SUBJECT_SCREENING_MODEL="visit_schedule_app.subjectscreening",
)
class EdcCrfTestCase(TestCase):
    helper_cls = Helper

    @classmethod
    def setUpClass(cls):
        import_holidays()
        return super().setUpClass()

    def setUp(self):
        self.subject_identifier = "12345"
        site_consents.registry = {}
        site_consents.register(v1_consent)
        self.helper = self.helper_cls(
            subject_identifier=self.subject_identifier,
            subject_consent_model_cls=SubjectConsent,
            onschedule_model_name="visit_schedule_app.onschedule",
        )
        site_visit_schedules._registry = {}
        site_visit_schedules.register(visit_schedule=visit_schedule)
        site_reference_configs.register_from_visit_schedule(
            visit_models={"edc_appointment.appointment": "edc_visit_tracking.subjectvisit"}
        )
        self.helper.consent_and_put_on_schedule()
        appointment = Appointment.objects.all()[0]
        self.subject_visit = SubjectVisit.objects.create(
            appointment=appointment, report_datetime=get_utcnow(), reason=SCHEDULED
        )

    def test_default_incomplete(self):
        crf_obj = Crf.objects.create(subject_visit=self.subject_visit)
        self.assertEqual(crf_obj.crf_status, INCOMPLETE)

    @override_settings(CRF_STATUS_DEFAULT=COMPLETE)
    def test_default_complete(self):
        crf_obj = Crf.objects.create(subject_visit=self.subject_visit)
        self.assertEqual(crf_obj.crf_status, COMPLETE)

    def test_creates_crf_status(self):
        crf_obj = Crf.objects.create(subject_visit=self.subject_visit)
        try:
            CrfStatus.objects.get(
                subject_identifier=crf_obj.subject_visit.subject_identifier,
                label_lower="edc_crf.crf",
            )
        except ObjectDoesNotExist:
            self.fail("crf status unexpectedly does not exist")

    def test_deletes_crf_status(self):
        crf_obj = Crf.objects.create(subject_visit=self.subject_visit)
        self.assertEqual(crf_obj.crf_status, INCOMPLETE)
        crf_obj.crf_status = COMPLETE
        crf_obj.save()
        self.assertRaises(
            ObjectDoesNotExist,
            CrfStatus.objects.get,
            subject_identifier=crf_obj.subject_visit.subject_identifier,
            label_lower="edc_crf.crf",
        )
