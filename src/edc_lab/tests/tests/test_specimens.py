from django.conf import settings
from django.contrib.sites.models import Site
from django.test import override_settings, TestCase, tag  # noqa
from edc_appointment.models import Appointment
from edc_constants.constants import YES, NO
from edc_facility import import_holidays
from edc_lab.identifiers import AliquotIdentifier as AliquotIdentifierBase
from edc_lab.lab import AliquotCreator as AliquotCreatorBase
from edc_lab.lab import AliquotType, Process, ProcessingProfile
from edc_lab.lab import Specimen as SpecimenBase, SpecimenNotDrawnError
from edc_lab.lab import SpecimenProcessor
from edc_lab.models import Aliquot
from edc_sites import add_or_update_django_sites
from edc_sites.single_site import SingleSite
from edc_sites.tests import SiteTestCaseMixin
from edc_utils.date import get_utcnow
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED
from multisite import SiteID

from ..models import SubjectRequisition, SubjectVisit, SubjectConsent
from ..site_labs_test_helper import SiteLabsTestHelper
from ..visit_schedules import visit_schedule


class AliquotIdentifier(AliquotIdentifierBase):
    identifier_length = 18


class AliquotCreator(AliquotCreatorBase):
    aliquot_identifier_cls = AliquotIdentifier


class Specimen(SpecimenBase):
    aliquot_creator_cls = AliquotCreator


class TestSpecimen(SiteTestCaseMixin, TestCase):

    lab_helper = SiteLabsTestHelper()

    @classmethod
    def setUpClass(cls):
        add_or_update_django_sites(
            sites=[
                SingleSite(
                    settings.SITE_ID,
                    "test_site",
                    country_code="ug",
                    country="uganda",
                    domain="bugamba.ug.clinicedc.org",
                )
            ]
        )
        import_holidays()
        return super().setUpClass()

    def setUp(self):
        site_visit_schedules._registry = {}
        site_visit_schedules.register(visit_schedule)
        self.subject_identifier = "1111111111"
        self.lab_helper.setup_site_labs()
        self.panel = self.lab_helper.panel
        SubjectConsent.objects.create(
            subject_identifier=self.subject_identifier,
            consent_datetime=get_utcnow(),
            identity="1111111",
            confirm_identity="1111111",
            visit_schedule_name="visit_schedule",
            schedule_name="schedule",
            site=Site.objects.get_current(),
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


class TestSpecimen2(SiteTestCaseMixin, TestCase):

    lab_helper = SiteLabsTestHelper()

    @classmethod
    def setUpClass(cls):
        add_or_update_django_sites(
            sites=[
                SingleSite(
                    settings.SITE_ID,
                    "test_site",
                    country_code="ug",
                    country="uganda",
                    domain="bugamba.ug.clinicedc.org",
                )
            ]
        )
        import_holidays()
        return super().setUpClass()

    def setUp(self):
        self.lab_helper.setup_site_labs()
        self.panel = self.lab_helper.panel
        self.profile_aliquot_count = self.lab_helper.profile_aliquot_count
        self.subject_identifier = "1111111111"
        Site.objects.get_current()
        SubjectConsent.objects.create(
            subject_identifier=self.subject_identifier,
            consent_datetime=get_utcnow(),
            identity="1111111",
            confirm_identity="1111111",
            visit_schedule_name="visit_schedule",
            schedule_name="schedule",
        )
        appointment = Appointment.objects.get(visit_code="1000")
        self.subject_visit = SubjectVisit.objects.create(
            appointment=appointment, report_datetime=get_utcnow(), reason=SCHEDULED
        )
        self.requisition = SubjectRequisition.objects.create(
            subject_visit=self.subject_visit,
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
        self.assertEqual(
            specimen.aliquots[0].aliquot_identifier, obj.aliquot_identifier
        )

    def test_process_repr(self):
        a = AliquotType(name="aliquot_a", numeric_code="55", alpha_code="AA")
        process = Process(aliquot_type=a)
        self.assertTrue(repr(process))

    def test_process_profile_repr(self):
        a = AliquotType(name="aliquot_a", numeric_code="55", alpha_code="AA")
        processing_profile = ProcessingProfile(
            name="processing_profile", aliquot_type=a
        )
        self.assertTrue(repr(processing_profile))

    def test_specimen_process(self):
        """Asserts calling process creates the correct number
        of child aliquots.
        """
        self.assertEqual(self.specimen.aliquots.count(), 1)
        self.specimen.process()
        self.assertEqual(self.specimen.aliquots.count(), self.profile_aliquot_count + 1)

    def test_specimen_process2(self):
        """Asserts calling process more than once has no effect.
        """
        self.specimen.process()
        self.assertEqual(self.specimen.aliquots.count(), self.profile_aliquot_count + 1)
        self.specimen.process()
        self.specimen.process()
        self.assertEqual(self.specimen.aliquots.count(), self.profile_aliquot_count + 1)

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
        """Assert all aliquots have correct 4 chars parent_segment.
        """
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
        """
        self.specimen.process()

        aliquot = self.specimen.aliquots.order_by("count")[0]
        self.assertTrue(aliquot.is_primary)
        self.assertEqual("5501", aliquot.aliquot_identifier[-4:])

        for index, aliquot in enumerate(self.specimen.aliquots.order_by("count")[1:]):
            index += 2
            self.assertFalse(aliquot.is_primary)
            self.assertEqual(
                f"66{str(index).zfill(2)}", aliquot.aliquot_identifier[-4:]
            )
