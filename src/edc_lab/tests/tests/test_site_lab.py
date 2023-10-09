import re

from django.conf import settings
from django.test import TestCase
from edc_appointment.models import Appointment
from edc_appointment.tests.helper import Helper
from edc_constants.constants import NO, NOT_APPLICABLE, YES
from edc_facility import import_holidays
from edc_sites import add_or_update_django_sites
from edc_sites.single_site import SingleSite
from edc_utils.date import get_utcnow
from edc_visit_tracking.constants import SCHEDULED

from edc_lab.lab import (
    AliquotType,
    LabProfile,
    Process,
    ProcessingProfile,
    ProcessingProfileAlreadyAdded,
)
from edc_lab.site_labs import SiteLabs, site_labs
from lab_app.models import SubjectRequisition, SubjectVisit

from ..site_labs_test_helper import SiteLabsTestHelper


class TestSiteLab(TestCase):
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
        return super().setUpClass()

    def test_site_labs(self):
        site_lab = SiteLabs()
        self.assertFalse(site_lab.loaded)

    def test_site_labs_register(self):
        lab_profile = LabProfile(
            name="lab_profile", requisition_model="edc_lab.subjectrequisition"
        )
        site_lab = SiteLabs()
        site_lab.register(lab_profile)
        self.assertTrue(site_lab.loaded)

    def test_site_labs_register_none(self):
        site_lab = SiteLabs()
        site_lab.register(None)
        self.assertFalse(site_lab.loaded)


class TestSiteLab2(TestCase):
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
        self.lab_profile = self.lab_helper.lab_profile
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

    def test_site_lab_panels(self):
        self.assertIn(self.panel.name, site_labs.get(self.lab_profile.name).panels)

    def test_panel_repr(self):
        self.assertTrue(repr(self.panel))

    def test_assert_cannot_add_duplicate_process(self):
        a = AliquotType(name="aliquot_a", numeric_code="55", alpha_code="AA")
        b = AliquotType(name="aliquot_b", numeric_code="66", alpha_code="BB")
        a.add_derivatives(b)
        process = Process(aliquot_type=b, aliquot_count=3)
        processing_profile = ProcessingProfile(name="process", aliquot_type=a)
        processing_profile.add_processes(process)
        self.assertRaises(
            ProcessingProfileAlreadyAdded, processing_profile.add_processes, process
        )

    def test_requisition_specimen(self):
        """Asserts can create a requisition."""
        SubjectRequisition.objects.create(
            subject_visit=self.subject_visit, panel=self.panel.panel_model_obj
        )

    def test_requisition_identifier2(self):
        """Asserts requisition identifier is set on requisition."""
        requisition = SubjectRequisition.objects.create(
            subject_visit=self.subject_visit,
            panel=self.panel.panel_model_obj,
            is_drawn=YES,
        )
        pattern = re.compile("[0-9]{2}[A-Z0-9]{5}")
        self.assertTrue(pattern.match(requisition.requisition_identifier))

    def test_requisition_identifier3(self):
        """Asserts requisition identifier is NOT set on requisition
        if specimen not drawn.
        """
        requisition = SubjectRequisition.objects.create(
            subject_visit=self.subject_visit,
            panel=self.panel.panel_model_obj,
            is_drawn=NO,
            reason_not_drawn=NOT_APPLICABLE,
        )
        # is never None, even if not drawn.
        self.assertIsNotNone(requisition.requisition_identifier)
        # if not drawn, format is not UUID
        pattern = re.compile("^[0-9]{2}[A-Z0-9]{5}$")
        self.assertFalse(pattern.match(requisition.requisition_identifier))

    def test_requisition_identifier5(self):
        """Asserts requisition identifier is set if specimen
        changed to drawn.
        """
        requisition = SubjectRequisition.objects.create(
            subject_visit=self.subject_visit,
            panel=self.panel.panel_model_obj,
            is_drawn=NO,
        )
        requisition.is_drawn = YES
        requisition.save()
        pattern = re.compile("[0-9]{2}[A-Z0-9]{5}")
        self.assertTrue(pattern.match(requisition.requisition_identifier))

    def test_requisition_identifier6(self):
        """Asserts requisition identifier is unchanged on save/resave."""
        requisition = SubjectRequisition.objects.create(
            subject_visit=self.subject_visit,
            panel=self.panel.panel_model_obj,
            is_drawn=YES,
        )
        requisition_identifier = requisition.requisition_identifier
        requisition.is_drawn = YES
        requisition.save()
        self.assertEqual(requisition_identifier, requisition.requisition_identifier)
