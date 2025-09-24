from datetime import datetime
from zoneinfo import ZoneInfo

import time_machine
from clinicedc_tests.consents import consent_v1
from clinicedc_tests.helper import Helper
from clinicedc_tests.labs import lab_profile, vl_panel
from clinicedc_tests.mixins import SiteTestCaseMixin
from clinicedc_tests.models import SubjectRequisition
from clinicedc_tests.sites import all_sites
from clinicedc_tests.visit_schedules.visit_schedule import get_visit_schedule
from django.test import TestCase, override_settings, tag
from django.utils import timezone

from edc_appointment.models import Appointment
from edc_consent import site_consents
from edc_constants.constants import NO, YES
from edc_facility.import_holidays import import_holidays
from edc_lab import site_labs
from edc_lab.identifiers import AliquotIdentifier as AliquotIdentifierBase
from edc_lab.lab import AliquotCreator as AliquotCreatorBase
from edc_lab.lab import Specimen as SpecimenBase
from edc_lab.lab import SpecimenNotDrawnError, SpecimenProcessor
from edc_sites.site import sites as site_sites
from edc_sites.utils import add_or_update_django_sites
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED
from edc_visit_tracking.models import SubjectVisit


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
    @classmethod
    def setUpTestData(cls):
        import_holidays()
        site_sites._registry = {}
        site_sites.loaded = False
        site_sites.register(*all_sites)
        add_or_update_django_sites()

    def setUp(self):
        site_labs.initialize()
        site_labs.register(lab_profile=lab_profile)

        site_consents.registry = {}
        site_consents.register(consent_v1)

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
            appointment=appointment, report_datetime=timezone.now(), reason=SCHEDULED
        )

        # use the viral load panel from the lap profile for these tests
        # vl_panel differs from default and has processes added to the ProcessingPanel
        # note also VL RequisitionPanel is added in the visit_schedule.schedule.requisitions
        self.panel = vl_panel  # RequisitionPanel

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
