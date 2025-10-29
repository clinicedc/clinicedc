from datetime import datetime
from zoneinfo import ZoneInfo

import time_machine
from clinicedc_constants import YES
from clinicedc_tests.consents import consent_v1
from clinicedc_tests.helper import Helper
from clinicedc_tests.labs import lab_profile, vl_panel
from clinicedc_tests.models import SubjectRequisition
from clinicedc_tests.sites import all_sites
from clinicedc_tests.visit_schedules.visit_schedule import get_visit_schedule
from django.test import TestCase, override_settings, tag
from django.utils import timezone

from edc_appointment.models import Appointment
from edc_consent import site_consents
from edc_facility.import_holidays import import_holidays
from edc_lab.identifiers import AliquotIdentifier as AliquotIdentifierBase
from edc_lab.lab import AliquotCreator as AliquotCreatorBase
from edc_lab.lab import AliquotType, Process, ProcessingProfile
from edc_lab.lab import Specimen as SpecimenBase
from edc_lab.models import Aliquot
from edc_lab.site_labs import site_labs
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
class TestSpecimen2(TestCase):
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
            consent_definition=consent_v1,
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

        self.requisition = SubjectRequisition.objects.create(
            subject_visit=self.subject_visit,
            requisition_datetime=timezone.now(),
            panel=self.panel.panel_model_obj,
            protocol_number="999",
            is_drawn=YES,
        )
        self.specimen = Specimen(requisition=self.requisition)

    def test_requisition_creates_aliquot(self):
        """Asserts passing requisition to specimen class
        creates an aliquot.
        """
        requisition = SubjectRequisition.objects.get(pk=self.requisition.pk)
        self.assertEqual(
            Aliquot.objects.filter(
                requisition_identifier=requisition.requisition_identifier,
                is_primary=True,
            ).count(),
            1,
        )

    def test_requisition_gets_aliquot(self):
        """Asserts passing requisition to specimen class gets
        an existing aliquot.
        """
        # instantiate again, to get primary aliquot
        specimen = Specimen(requisition=self.requisition)
        obj = Aliquot.objects.get(
            requisition_identifier=self.requisition.requisition_identifier,
            is_primary=True,
        )
        self.assertEqual(specimen.aliquots[0].aliquot_identifier, obj.aliquot_identifier)

    def test_process_repr(self):
        a = AliquotType(name="aliquot_a", numeric_code="02", alpha_code="WB")
        process = Process(aliquot_type=a)
        self.assertTrue(repr(process))

    def test_process_profile_repr(self):
        a = AliquotType(name="aliquot_a", numeric_code="02", alpha_code="WB")
        processing_profile = ProcessingProfile(name="processing_profile", aliquot_type=a)
        self.assertTrue(repr(processing_profile))

    def test_specimen_process(self):
        """Asserts calling process creates the correct number
        of child aliquots.
        """
        self.assertEqual(self.specimen.aliquots.count(), 1)
        self.specimen.process()  # WB
        self.assertEqual(self.specimen.aliquots.count(), 1 + 2 + 4)  # WB, PL, BC

    def test_specimen_process2(self):
        """Asserts calling process more than once has no effect."""
        self.specimen.process()
        self.assertEqual(self.specimen.aliquots.count(), 1 + 2 + 4)  # WB, PL, BC
        self.specimen.process()
        self.specimen.process()
        self.assertEqual(self.specimen.aliquots.count(), 1 + 2 + 4)  # WB, PL, BC

    def test_specimen_process_identifier_prefix(self):
        """Assert all aliquots start with the correct identifier
        prefix.
        """
        self.specimen.process()
        for aliquot in self.specimen.aliquots.order_by("created"):
            self.assertIn(
                self.specimen.primary_aliquot.identifier_prefix,
                aliquot.aliquot_identifier,
            )

    def test_specimen_process_identifier_parent_segment(self):
        """Assert all aliquots have correct 4 chars parent_segment."""
        self.specimen.process()
        parent_segment = self.specimen.primary_aliquot.aliquot_identifier[-4:]

        aliquot = self.specimen.aliquots.order_by("count")[0]
        self.assertTrue(aliquot.is_primary)
        self.assertEqual("0000", aliquot.aliquot_identifier[-8:-4])

        for aliquot in self.specimen.aliquots.order_by("count")[1:]:
            self.assertFalse(aliquot.is_primary)
            self.assertEqual(parent_segment, aliquot.aliquot_identifier[-8:-4])

    def test_specimen_process_identifier_child_segment(self):
        """Assert all aliquots have correct 4 chars child_segment.

        Last digit maintains a sequential number where 1 is the
        primary and anything >1 is a derivative of the primary

        In this case, the last buffy coat aliquot ends in 7
        meaning there are 7 tubes, primary + 6 derivatives or
        4 plasma and 3 buffy coat as configured in the process
        (See lap_profile.processing_profile.processes) or
        the lab_profile from clinicedc_tests.labs
        """
        self.specimen.process()

        # primary aliquot ending on 1
        aliquot = self.specimen.aliquots.order_by("count")[0]
        self.assertTrue(aliquot.is_primary)
        self.assertEqual("0201", aliquot.aliquot_identifier[-4:])

        # plasma: 4 aliquots where seq fragment start w/ 36
        # ending in 2,3,4,5
        pl_aliquots = []
        for aliquot in self.specimen.aliquots.order_by("-aliquot_identifier"):
            if aliquot.aliquot_identifier[-4:].startswith("36"):
                pl_aliquots.append(aliquot)  # noqa: PERF401
        pl_aliquots.reverse()
        for i in range(0, 3):
            self.assertFalse(pl_aliquots[i].is_primary)
            self.assertEqual(
                f"36{str(i + 2).zfill(2)}", pl_aliquots[i].aliquot_identifier[-4:]
            )

        # buffy coat: 2 aliquots where seq fragment start w/ 12
        # ending in 6,7
        bc_aliquots = []
        for aliquot in self.specimen.aliquots.order_by("-aliquot_identifier"):
            if aliquot.aliquot_identifier[-4:].startswith("12"):
                bc_aliquots.append(aliquot)  # noqa: PERF401
        bc_aliquots.reverse()
        for i in range(0, 2):
            self.assertFalse(bc_aliquots[i].is_primary)
            self.assertEqual(
                f"12{str(i + 6).zfill(2)}", bc_aliquots[i].aliquot_identifier[-4:]
            )
