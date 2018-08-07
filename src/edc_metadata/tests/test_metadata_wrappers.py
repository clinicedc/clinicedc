from django.test import TestCase, tag
from edc_appointment.models import Appointment
from edc_base import get_utcnow
from edc_facility.import_holidays import import_holidays
from edc_lab.models.panel import Panel
from edc_reference import site_reference_configs
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED

from ..metadata_wrappers import RequisitionMetadataWrapper, CrfMetadataWrapper
from ..metadata_wrappers import MetadataWrapperError
from ..metadata_wrappers import RequisitionMetadataWrappers, CrfMetadataWrappers
from ..models import CrfMetadata, RequisitionMetadata
from .models import SubjectConsent, SubjectVisit, CrfOne, SubjectRequisition
from .reference_configs import register_to_site_reference_configs
from .visit_schedule import visit_schedule


class TestMetadataWrapperObjects(TestCase):

    def setUp(self):
        import_holidays()
        self.panel_one = Panel.objects.create(name='one')
        register_to_site_reference_configs()
        site_visit_schedules._registry = {}
        site_visit_schedules.loaded = False
        site_visit_schedules.register(visit_schedule)
        site_reference_configs.register_from_visit_schedule(
            visit_models={
                'edc_appointment.appointment': 'edc_metadata.subjectvisit'})
        self.subject_identifier = '1111111'
        subject_consent = SubjectConsent.objects.create(
            subject_identifier=self.subject_identifier,
            consent_datetime=get_utcnow())
        _, self.schedule = site_visit_schedules.get_by_onschedule_model(
            'edc_metadata.onschedule')
        self.schedule.put_on_schedule(
            subject_identifier=self.subject_identifier,
            onschedule_datetime=subject_consent.consent_datetime)
        self.appointment = Appointment.objects.get(
            subject_identifier=self.subject_identifier,
            visit_code=self.schedule.visits.first.code)
        self.subject_visit = SubjectVisit.objects.create(
            appointment=self.appointment,
            subject_identifier=self.subject_identifier,
            reason=SCHEDULED)

    def test_crf_metadata_wrapper_none(self):
        metadata_obj = CrfMetadata.objects.get(
            subject_identifier=self.subject_identifier,
            model='edc_metadata.crfone')
        crf_metadata_wrapper = CrfMetadataWrapper(
            visit=self.subject_visit,
            metadata_obj=metadata_obj)
        self.assertEqual(crf_metadata_wrapper.model_cls, CrfOne)
        self.assertEqual(crf_metadata_wrapper.model_obj, None)
        self.assertEqual(crf_metadata_wrapper.metadata_obj, metadata_obj)
        self.assertEqual(crf_metadata_wrapper.visit, self.subject_visit)

    def test_crf_metadata_wrapper_exists(self):
        model_obj = CrfOne.objects.create(
            subject_visit=self.subject_visit)
        metadata_obj = CrfMetadata.objects.get(
            subject_identifier=self.subject_identifier,
            model='edc_metadata.crfone')
        crf_metadata_wrapper = CrfMetadataWrapper(
            visit=self.subject_visit,
            metadata_obj=metadata_obj)
        self.assertEqual(crf_metadata_wrapper.model_cls, CrfOne)
        self.assertEqual(crf_metadata_wrapper.model_obj, model_obj)
        self.assertEqual(crf_metadata_wrapper.metadata_obj, metadata_obj)
        self.assertEqual(crf_metadata_wrapper.visit, self.subject_visit)

    def test_requisition_metadata_wrapper_none(self):
        metadata_obj = RequisitionMetadata.objects.get(
            subject_identifier=self.subject_identifier,
            model='edc_metadata.subjectrequisition',
            panel_name=self.panel_one.name)
        requisition_metadata_wrapper = RequisitionMetadataWrapper(
            visit=self.subject_visit,
            metadata_obj=metadata_obj)
        self.assertEqual(
            requisition_metadata_wrapper.model_cls, SubjectRequisition)
        self.assertEqual(requisition_metadata_wrapper.model_obj, None)
        self.assertEqual(
            requisition_metadata_wrapper.metadata_obj, metadata_obj)
        self.assertEqual(requisition_metadata_wrapper.visit,
                         self.subject_visit)

    def test_requisition_metadata_wrapper_exists(self):
        model_obj = SubjectRequisition.objects.create(
            subject_visit=self.subject_visit,
            panel=self.panel_one)
        metadata_obj = RequisitionMetadata.objects.get(
            subject_identifier=self.subject_identifier,
            model='edc_metadata.subjectrequisition',
            panel_name=self.panel_one.name)
        requisition_metadata_wrapper = RequisitionMetadataWrapper(
            visit=self.subject_visit,
            metadata_obj=metadata_obj)
        self.assertEqual(
            requisition_metadata_wrapper.model_cls, SubjectRequisition)
        self.assertEqual(requisition_metadata_wrapper.model_obj, model_obj)
        self.assertEqual(
            requisition_metadata_wrapper.metadata_obj, metadata_obj)
        self.assertEqual(requisition_metadata_wrapper.visit,
                         self.subject_visit)

    def test_crf_metadata_wrapper_raises_on_invalid_model(self):
        metadata_obj = CrfMetadata.objects.create(
            subject_identifier=self.subject_identifier,
            model='edc_metadata.blah',
            show_order=9999)
        self.assertRaises(
            MetadataWrapperError,
            CrfMetadataWrapper,
            visit=self.subject_visit,
            metadata_obj=metadata_obj)

    def test_crf_metadata_wrapper_raises_on_missing_crf_model_manager(self):
        metadata_obj = CrfMetadata.objects.create(
            subject_identifier=self.subject_identifier,
            model='edc_metadata.crfmissingmanager',
            show_order=9999)
        self.assertRaises(
            MetadataWrapperError,
            CrfMetadataWrapper,
            visit=self.subject_visit,
            metadata_obj=metadata_obj)

    def test_get_crfs(self):
        crf_metadata_wrappers = CrfMetadataWrappers(
            appointment=self.appointment)
        self.assertEqual(len(crf_metadata_wrappers.objects), 5)

    def test_get_requisitions(self):
        requisition_metadata_wrappers = RequisitionMetadataWrappers(
            appointment=self.appointment)
        self.assertEqual(len(requisition_metadata_wrappers.objects), 6)
