from django.test import TestCase, override_settings
from edc_appointment.models import Appointment
from edc_appointment.tests.helper import Helper
from edc_constants.constants import NO, YES
from edc_facility import import_holidays
from edc_sites.tests import SiteTestCaseMixin
from edc_utils.date import get_utcnow
from edc_visit_tracking.constants import SCHEDULED

from edc_lab.identifiers import AliquotIdentifier as AliquotIdentifierBase
from edc_lab.lab import AliquotCreator as AliquotCreatorBase
from edc_lab.lab import Specimen as SpecimenBase
from edc_lab.lab import SpecimenNotDrawnError, SpecimenProcessor
from lab_app.models import SubjectRequisition, SubjectVisit

from ..site_labs_test_helper import SiteLabsTestHelper


class AliquotIdentifier(AliquotIdentifierBase):
    identifier_length = 18


class AliquotCreator(AliquotCreatorBase):
    aliquot_identifier_cls = AliquotIdentifier


class Specimen(SpecimenBase):
    aliquot_creator_cls = AliquotCreator


@override_settings(SITE_ID=10)
class TestSpecimen(SiteTestCaseMixin, TestCase):
    lab_helper = SiteLabsTestHelper()

    @classmethod
    def setUpTestData(cls):
        import_holidays()

    def setUp(self):
        self.lab_helper.setup_site_labs()
        self.panel = self.lab_helper.panel
        self.subject_identifier = "1111111111"
        self.helper = Helper(subject_identifier=self.subject_identifier)
        self.helper.consent_and_put_on_schedule(
            visit_schedule_name="visit_schedule",
            schedule_name="schedule",
            age_in_years=25,
        )
        appointment = Appointment.objects.get(visit_code="1000")
        self.subject_visit = SubjectVisit.objects.create(
            appointment=appointment, report_datetime=get_utcnow(), reason=SCHEDULED
        )

    def test_specimen_processor(self):
        SpecimenProcessor(aliquot_creator_cls=AliquotCreator)

    def test_specimen(self):
        requisition = SubjectRequisition.objects.create(
            subject_visit=self.subject_visit,
            panel=self.panel.panel_model_obj,
            protocol_number="999",
            is_drawn=YES,
        )
        Specimen(requisition=requisition)

    def test_specimen_repr(self):
        requisition = SubjectRequisition.objects.create(
            subject_visit=self.subject_visit,
            panel=self.panel.panel_model_obj,
            protocol_number="999",
            is_drawn=YES,
        )
        specimen = Specimen(requisition=requisition)
        self.assertTrue(repr(specimen))

    def test_specimen_from_pk(self):
        requisition = SubjectRequisition.objects.create(
            subject_visit=self.subject_visit,
            panel=self.panel.panel_model_obj,
            protocol_number="999",
            is_drawn=YES,
        )
        Specimen(requisition=requisition)

    def test_specimen_not_drawn(self):
        requisition = SubjectRequisition.objects.create(
            subject_visit=self.subject_visit,
            panel=self.panel.panel_model_obj,
            protocol_number="999",
            is_drawn=NO,
        )
        self.assertRaises(SpecimenNotDrawnError, Specimen, requisition=requisition)
