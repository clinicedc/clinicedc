from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase, override_settings
from edc_appointment.models import Appointment
from edc_consent.site_consents import site_consents
from edc_constants.constants import COMPLETE, INCOMPLETE
from edc_facility import import_holidays
from edc_utils import get_utcnow
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED
from edc_visit_tracking.tests.helper import Helper
from visit_schedule_app.models import SubjectVisit

from edc_crf.models import CrfStatus

from ..consents import consent_v1
from ..models import Crf
from ..visit_schedule import visit_schedule


@override_settings(
    SUBJECT_SCREENING_MODEL="edc_crf.subjectscreening",
    SITE_ID=10,
)
class CrfTestCase(TestCase):
    helper_cls = Helper

    @classmethod
    def setUpTestData(cls):
        import_holidays()

    def setUp(self):
        self.subject_identifier = "12345"
        site_consents.registry = {}
        site_consents.register(consent_v1)
        self.helper = self.helper_cls(subject_identifier=self.subject_identifier)
        site_visit_schedules._registry = {}
        site_visit_schedules.register(visit_schedule=visit_schedule)
        self.helper.consent_and_put_on_schedule(
            visit_schedule_name="visit_schedule",
            schedule_name="schedule",
        )
        appointment = Appointment.objects.all().order_by("timepoint", "visit_code_sequence")[0]
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
