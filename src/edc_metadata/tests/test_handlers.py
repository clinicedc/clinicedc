from django.test import TestCase
from edc_appointment.models import Appointment
from edc_facility.import_holidays import import_holidays
from edc_lab.models.panel import Panel
from edc_reference.site_reference import site_reference_configs
from edc_utils import get_utcnow
from edc_visit_schedule import site_visit_schedules
from edc_visit_tracking.constants import MISSED_VISIT, SCHEDULED

from ..models import CrfMetadata, RequisitionMetadata
from ..requisition import InvalidTargetPanel, TargetPanelNotScheduledForVisit
from ..requisition import RequisitionTargetHandler
from ..target_handler import TargetModelLookupError, TargetHandler
from ..target_handler import TargetModelNotScheduledForVisit
from .models import SubjectVisit, SubjectConsent
from .reference_configs import register_to_site_reference_configs
from .visit_schedule import visit_schedule


class TestHandlers(TestCase):
    @classmethod
    def setUpClass(cls):
        import_holidays()
        return super(TestHandlers, cls).setUpClass()

    def setUp(self):
        self.panel_one = Panel.objects.create(name="one")
        self.panel_seven = Panel.objects.create(name="seven")
        self.panel_blah = Panel.objects.create(name="blah")
        register_to_site_reference_configs()
        site_visit_schedules._registry = {}
        site_visit_schedules.loaded = False
        site_visit_schedules.register(visit_schedule)
        site_reference_configs.register_from_visit_schedule(
            visit_models={"edc_appointment.appointment": "edc_metadata.subjectvisit"}
        )
        self.subject_identifier = "1111111"
        self.assertEqual(CrfMetadata.objects.all().count(), 0)
        self.assertEqual(RequisitionMetadata.objects.all().count(), 0)
        subject_consent = SubjectConsent.objects.create(
            subject_identifier=self.subject_identifier, consent_datetime=get_utcnow()
        )
        _, self.schedule = site_visit_schedules.get_by_onschedule_model(
            "edc_metadata.onschedule"
        )
        self.schedule.put_on_schedule(
            subject_identifier=self.subject_identifier,
            onschedule_datetime=subject_consent.consent_datetime,
        )
        self.appointment = Appointment.objects.get(
            subject_identifier=self.subject_identifier,
            visit_code=self.schedule.visits.first.code,
        )

    def test_requisition_handler_invalid_target_panel(self):
        visit_model_instance = SubjectVisit.objects.create(
            appointment=self.appointment, reason=SCHEDULED
        )
        self.assertRaises(
            InvalidTargetPanel,
            RequisitionTargetHandler,
            model="edc_metadata.subjectrequisition",
            visit_model_instance=visit_model_instance,
            target_panel=self.panel_blah,
        )

    def test_requisition_handler_target_panel_not_for_visit(self):
        visit_model_instance = SubjectVisit.objects.create(
            appointment=self.appointment, reason=SCHEDULED
        )
        self.assertRaises(
            TargetPanelNotScheduledForVisit,
            RequisitionTargetHandler,
            model="edc_metadata.subjectrequisition",
            visit_model_instance=visit_model_instance,
            target_panel=self.panel_seven,
        )

    def test_crf_handler_invalid_target_model(self):
        visit_model_instance = SubjectVisit.objects.create(
            appointment=self.appointment, reason=SCHEDULED
        )
        self.assertRaises(
            TargetModelLookupError,
            TargetHandler,
            model="edc_metadata.crfblah",
            visit_model_instance=visit_model_instance,
        )

    def test_crf_handler_target_model_not_for_visit(self):
        visit_model_instance = SubjectVisit.objects.create(
            appointment=self.appointment, reason=SCHEDULED
        )
        self.assertRaises(
            TargetModelNotScheduledForVisit,
            TargetHandler,
            model="edc_metadata.crfseven",
            visit_model_instance=visit_model_instance,
        )

    def test_crf_handler_target_model_ignored_for_missed_visit(self):
        visit_model_instance = SubjectVisit.objects.create(
            appointment=self.appointment, reason=MISSED_VISIT
        )
        try:
            TargetHandler(
                model="edc_metadata.crfseven",
                visit_model_instance=visit_model_instance,
            )
        except TargetModelNotScheduledForVisit:
            self.fail("TargetModelNotScheduledForVisit unexpectedly raised")
