from django.test import TestCase, tag

from edc_appointment.models import Appointment
from edc_registration.models import RegisteredSubject
from edc_visit_schedule import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED

from ..constants import REQUISITION, CRF
from ..models import CrfMetadata, RequisitionMetadata
from ..requisition import InvalidTargetPanel, TargetPanelNotScheduledForVisit
from ..requisition import RequisitionTargetHandler
from ..target_handler import TargetModelLookupError, TargetHandler
from ..target_handler import TargetModelNotScheduledForVisit
from .models import SubjectVisit, Enrollment
from .reference_configs import register_to_site_reference_configs
from .visit_schedule import visit_schedule


class TestHandlers(TestCase):

    def setUp(self):
        register_to_site_reference_configs()
        site_visit_schedules._registry = {}
        site_visit_schedules.loaded = False
        site_visit_schedules.register(visit_schedule)
        self.schedule = site_visit_schedules.get_schedule(
            visit_schedule_name='visit_schedule',
            schedule_name='schedule')
        self.subject_identifier = '1111111'
        RegisteredSubject.objects.create(
            subject_identifier=self.subject_identifier)
        self.assertEqual(CrfMetadata.objects.all().count(), 0)
        self.assertEqual(RequisitionMetadata.objects.all().count(), 0)
        Enrollment.objects.create(subject_identifier=self.subject_identifier)
        self.appointment = Appointment.objects.get(
            subject_identifier=self.subject_identifier,
            visit_code=self.schedule.visits.first.code)

    def test_requisition_handler_invalid_target_panel(self):
        visit_obj = SubjectVisit.objects.create(
            appointment=self.appointment, reason=SCHEDULED)
        self.assertRaises(
            InvalidTargetPanel,
            RequisitionTargetHandler,
            model='edc_metadata.subjectrequisition',
            visit=visit_obj,
            target_panel='blah',
            metadata_category=REQUISITION)

    def test_requisition_handler_target_panel_not_for_visit(self):
        visit_obj = SubjectVisit.objects.create(
            appointment=self.appointment, reason=SCHEDULED)
        self.assertRaises(
            TargetPanelNotScheduledForVisit,
            RequisitionTargetHandler,
            model='edc_metadata.subjectrequisition',
            visit=visit_obj,
            target_panel='seven',
            metadata_category=REQUISITION)

    def test_crf_handler_invalid_target_model(self):
        visit_obj = SubjectVisit.objects.create(
            appointment=self.appointment, reason=SCHEDULED)
        self.assertRaises(
            TargetModelLookupError,
            TargetHandler,
            model='edc_metadata.crfblah',
            visit=visit_obj,
            metadata_category=CRF)

    def test_crf_handler_target_model_not_for_visit(self):
        visit_obj = SubjectVisit.objects.create(
            appointment=self.appointment, reason=SCHEDULED)
        self.assertRaises(
            TargetModelNotScheduledForVisit,
            TargetHandler,
            model='edc_metadata.crfseven',
            visit=visit_obj,
            metadata_category=CRF)
