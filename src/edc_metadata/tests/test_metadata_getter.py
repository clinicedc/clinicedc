from django.test import TestCase, tag
from edc_appointment.models import Appointment
from edc_utils import get_utcnow
from edc_facility.import_holidays import import_holidays
from edc_reference.site_reference import site_reference_configs
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED

from ..constants import REQUIRED
from ..metadata import CrfMetadataGetter
from ..models import CrfMetadata, RequisitionMetadata
from ..next_form_getter import NextFormGetter
from .models import SubjectVisit, SubjectConsent, CrfOne, CrfTwo
from .reference_configs import register_to_site_reference_configs
from .visit_schedule import visit_schedule


class TestMetadataGetter(TestCase):
    @classmethod
    def setUpClass(cls):
        import_holidays()
        return super(TestMetadataGetter, cls).setUpClass()

    def setUp(self):
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
        self.subject_visit = SubjectVisit.objects.create(
            appointment=self.appointment,
            subject_identifier=self.subject_identifier,
            reason=SCHEDULED,
        )

    def test_objects_none_no_appointment(self):
        subject_identifier = None
        visit_code = None
        getter = CrfMetadataGetter(
            subject_identifier=subject_identifier, visit_code=visit_code
        )
        self.assertEqual(getter.metadata_objects.count(), 0)

    def test_objects_not_none_without_appointment(self):
        getter = CrfMetadataGetter(
            subject_identifier=self.subject_identifier,
            visit_code=self.appointment.visit_code,
            visit_code_sequence=self.appointment.visit_code_sequence,
        )
        self.assertGreater(getter.metadata_objects.count(), 0)

    def test_objects_not_none_from_appointment(self):
        getter = CrfMetadataGetter(appointment=self.appointment)
        self.assertGreater(getter.metadata_objects.count(), 0)

    def test_next_object(self):
        getter = CrfMetadataGetter(appointment=self.appointment)
        visit = self.schedule.visits.get(getter.visit_code)
        objects = []
        for crf in visit.crfs:
            obj = getter.next_object(crf.show_order, entry_status=REQUIRED)
            if obj:
                objects.append(obj)
                self.assertIsNotNone(obj)
                self.assertGreater(obj.show_order, crf.show_order)
        self.assertEqual(len(objects), len(visit.crfs) - 1)

    def test_next_required_form(self):
        getter = NextFormGetter(
            appointment=self.appointment, model="edc_metadata.crftwo"
        )
        self.assertEqual(getter.next_form.model, "edc_metadata.crfthree")

    def test_next_required_form2(self):
        CrfOne.objects.create(subject_visit=self.subject_visit)
        crf_two = CrfTwo.objects.create(subject_visit=self.subject_visit)
        getter = NextFormGetter(model_obj=crf_two)
        self.assertEqual(getter.next_form.model, "edc_metadata.crfthree")

    def test_next_requisition(self):
        getter = NextFormGetter(
            appointment=self.appointment,
            model="edc_metadata.subjectrequisition",
            panel_name="one",
        )
        next_form = getter.next_form
        self.assertEqual(next_form.model, "edc_metadata.subjectrequisition")
        self.assertEqual(next_form.panel.name, "two")

    def test_next_requisition_if_last(self):
        getter = NextFormGetter(
            appointment=self.appointment,
            model="edc_metadata.subjectrequisition",
            panel_name="six",
        )
        next_form = getter.next_form
        self.assertIsNone(next_form)

    def test_next_requisition_if_not_in_visit(self):
        getter = NextFormGetter(
            appointment=self.appointment,
            model="edc_metadata.subjectrequisition",
            panel_name="blah",
        )
        next_form = getter.next_form
        self.assertIsNone(next_form)
