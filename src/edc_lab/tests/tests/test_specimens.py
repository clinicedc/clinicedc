from datetime import datetime
from zoneinfo import ZoneInfo

import time_machine
from django.test import TestCase, override_settings, tag

from edc_appointment.models import Appointment
from edc_constants.constants import NO, YES
from edc_facility.import_holidays import import_holidays
from edc_lab.identifiers import AliquotIdentifier as AliquotIdentifierBase
from edc_lab.lab import AliquotCreator as AliquotCreatorBase
from edc_lab.lab import Specimen as SpecimenBase
from edc_lab.lab import SpecimenNotDrawnError, SpecimenProcessor
from edc_sites.tests import SiteTestCaseMixin
from edc_utils.date import get_utcnow
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED
from edc_visit_tracking.models import SubjectVisit
from tests.consents import consent_v1
from tests.helper import Helper
from tests.models import SubjectRequisition
from tests.visit_schedules.visit_schedule import get_visit_schedule

from ..site_labs_test_helper import SiteLabsTestHelper


class AliquotIdentifier(AliquotIdentifierBase):
    identifier_length = 18


class AliquotCreator(AliquotCreatorBase):
    aliquot_identifier_cls = AliquotIdentifier


class Specimen(SpecimenBase):
    aliquot_creator_cls = AliquotCreator


utc_tz = ZoneInfo("UTC")


@tag("lab")
@override_settings(SITE_ID=10)
@time_machine.travel(datetime(2025, 6, 11, 8, 00, tzinfo=utc_tz))
class TestSpecimen(SiteTestCaseMixin, TestCase):
    lab_helper = SiteLabsTestHelper()

    @classmethod
    def setUpTestData(cls):
        import_holidays()

    def setUp(self):
        self.lab_helper.setup_site_labs()
        self.panel = self.lab_helper.panel

        site_visit_schedules._registry = {}
        site_visit_schedules.loaded = False
        site_visit_schedules.register(get_visit_schedule(consent_v1))

        self.helper = Helper()
        subject_consent = self.helper.consent_and_put_on_schedule(
            visit_schedule_name="visit_schedule",
            schedule_name="schedule",
            age_in_years=25,
        )
        self.subject_identifier = subject_consent.subject_identifier
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
