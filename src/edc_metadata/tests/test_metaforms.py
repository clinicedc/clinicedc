from collections import OrderedDict
from django.test import TestCase, tag

from edc_appointment.models import Appointment
from edc_registration.models import RegisteredSubject
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED

from ..metaforms import RequisitionMetaform, CrfMetaform
from ..metaforms import MetaformError
from ..metaforms import CrfMetaforms, RequisitionMetaforms
from ..models import CrfMetadata, RequisitionMetadata
from ..rules import site_metadata_rules
from .metadata_rules import register_to_site_reference_fields
from .models import Enrollment, SubjectVisit, CrfOne, SubjectRequisition
from .visit_schedule import visit_schedule


@tag('1')
class TestMetaformObjects(TestCase):

    def setUp(self):
        register_to_site_reference_fields()
        site_metadata_rules.registry = OrderedDict()

        site_visit_schedules._registry = {}
        site_visit_schedules.loaded = False
        site_visit_schedules.register(visit_schedule)
        self.schedule = site_visit_schedules.get_schedule(
            visit_schedule_name='visit_schedule',
            schedule_name='schedule')
        self.subject_identifier = '1111111'
        RegisteredSubject.objects.create(
            subject_identifier=self.subject_identifier)
        Enrollment.objects.create(subject_identifier=self.subject_identifier)
        self.appointment = Appointment.objects.get(
            subject_identifier=self.subject_identifier,
            visit_code=self.schedule.visits.first.code)
        self.subject_visit = SubjectVisit.objects.create(
            appointment=self.appointment,
            subject_identifier=self.subject_identifier,
            reason=SCHEDULED)

    def test_crf_metaform_none(self):
        metadata_obj = CrfMetadata.objects.get(
            subject_identifier=self.subject_identifier,
            model='edc_metadata.crfone')
        crf_metaform = CrfMetaform(
            visit=self.subject_visit,
            metadata_obj=metadata_obj)
        self.assertEqual(crf_metaform.model_cls, CrfOne)
        self.assertEqual(crf_metaform.model_obj, None)
        self.assertEqual(crf_metaform.metadata_obj, metadata_obj)
        self.assertEqual(crf_metaform.visit, self.subject_visit)

    def test_crf_metaform_exists(self):
        model_obj = CrfOne.objects.create(
            subject_visit=self.subject_visit)
        metadata_obj = CrfMetadata.objects.get(
            subject_identifier=self.subject_identifier,
            model='edc_metadata.crfone')
        crf_metaform = CrfMetaform(
            visit=self.subject_visit,
            metadata_obj=metadata_obj)
        self.assertEqual(crf_metaform.model_cls, CrfOne)
        self.assertEqual(crf_metaform.model_obj, model_obj)
        self.assertEqual(crf_metaform.metadata_obj, metadata_obj)
        self.assertEqual(crf_metaform.visit, self.subject_visit)

    def test_requisition_metaform_none(self):
        metadata_obj = RequisitionMetadata.objects.get(
            subject_identifier=self.subject_identifier,
            model='edc_metadata.subjectrequisition',
            panel_name='one')
        requisition_metaform = RequisitionMetaform(
            visit=self.subject_visit,
            metadata_obj=metadata_obj)
        self.assertEqual(requisition_metaform.model_cls, SubjectRequisition)
        self.assertEqual(requisition_metaform.model_obj, None)
        self.assertEqual(requisition_metaform.metadata_obj, metadata_obj)
        self.assertEqual(requisition_metaform.visit, self.subject_visit)

    def test_requisition_metaform_exists(self):
        model_obj = SubjectRequisition.objects.create(
            subject_visit=self.subject_visit,
            panel_name='one')
        metadata_obj = RequisitionMetadata.objects.get(
            subject_identifier=self.subject_identifier,
            model='edc_metadata.subjectrequisition',
            panel_name='one')
        requisition_metaform = RequisitionMetaform(
            visit=self.subject_visit,
            metadata_obj=metadata_obj)
        self.assertEqual(requisition_metaform.model_cls, SubjectRequisition)
        self.assertEqual(requisition_metaform.model_obj, model_obj)
        self.assertEqual(requisition_metaform.metadata_obj, metadata_obj)
        self.assertEqual(requisition_metaform.visit, self.subject_visit)

    def test_crf_metaform_raises_on_invalid_model(self):
        metadata_obj = CrfMetadata.objects.create(
            subject_identifier=self.subject_identifier,
            model='edc_metadata.blah',
            show_order=9999)
        self.assertRaises(
            MetaformError,
            CrfMetaform,
            visit=self.subject_visit,
            metadata_obj=metadata_obj)

    def test_crf_metaform_raises_on_missing_crf_model_manager(self):
        metadata_obj = CrfMetadata.objects.create(
            subject_identifier=self.subject_identifier,
            model='edc_metadata.crfmissingmanager',
            show_order=9999)
        self.assertRaises(
            MetaformError,
            CrfMetaform,
            visit=self.subject_visit,
            metadata_obj=metadata_obj)

    def test_get_crfs(self):
        crf_metaforms = CrfMetaforms(appointment=self.appointment)
        self.assertEqual(len(crf_metaforms.objects), 5)

    def test_get_requisitions(self):
        requisition_metaforms = RequisitionMetaforms(
            appointment=self.appointment)
        self.assertEqual(len(requisition_metaforms.objects), 6)
