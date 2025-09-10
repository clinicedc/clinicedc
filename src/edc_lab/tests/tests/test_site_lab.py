import re

from django.test import TestCase, override_settings, tag

from edc_appointment.models import Appointment
from edc_consent import site_consents
from edc_constants.constants import NO, NOT_APPLICABLE, YES
from edc_facility.import_holidays import import_holidays
from edc_lab.lab import (
    AliquotType,
    LabProfile,
    Process,
    ProcessingProfile,
    ProcessingProfileAlreadyAdded,
)
from edc_lab.site_labs import site_labs
from edc_sites.site import sites as site_sites
from edc_sites.utils import add_or_update_django_sites
from edc_utils.date import get_utcnow
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED
from edc_visit_tracking.models import SubjectVisit
from tests.consents import consent_v1
from tests.helper import Helper
from tests.labs import lab_profile, vl_panel
from tests.models import SubjectRequisition
from tests.sites import all_sites
from tests.visit_schedules.visit_schedule import get_visit_schedule


@tag("lab")
@override_settings(SITE_ID=10)
class TestSiteLab2(TestCase):

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

        self.panel = vl_panel  # RequisitionPanel

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
            appointment=appointment, report_datetime=get_utcnow(), reason=SCHEDULED
        )

    def test_site_labs(self):
        site_labs.initialize()
        self.assertFalse(site_labs.loaded)

    def test_site_labs_register(self):
        site_labs.initialize()
        lp = LabProfile(
            name="lab_profile", requisition_model="tests.subjectrequisition"
        )
        site_labs.register(lp)
        self.assertTrue(site_labs.loaded)

    def test_site_labs_register_none(self):
        site_labs.initialize()
        site_labs.register(None)
        self.assertFalse(site_labs.loaded)

    def test_site_lab_panels(self):
        self.assertIn(self.panel.name, site_labs.get(lab_profile.name).panels)

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
