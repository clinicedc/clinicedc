from django.apps import apps as django_apps
from django.utils import timezone

from edc_constants.constants import KEYED, UNKEYED, MISSED_VISIT
from edc_meta_data.models import LabEntry

from example.models import SubjectVisit, CrfOne  # TestPanel, TestAliquotType, CrfOne

# from .base_test_case import BaseTestCase
from django.test.testcases import TestCase


class TestMetaData(TestCase):

    @property
    def crf_meta_data_model(self):
        return django_apps.get_app_config('edc_meta_data').crf_meta_data_model

    @property
    def requisition_meta_data_model(self):
        return django_apps.get_app_config('edc_meta_data').requisition_meta_data_model

    def test_creates_meta_data1(self):
        """No meta data if visit tracking form is not entered."""
        self.assertEqual(self.crf_meta_data_model.objects.filter(
            registered_subject=self.registered_subject).count(), 0)

    def test_creates_requisition_meta_data(self):
        """Meta data is created when visit tracking form is added, each instance set to NEW."""
        self.assertTrue(LabEntry.objects.all().count() > 0)
        self.subject_visit = SubjectVisit.objects.create(
            appointment=self.appointment,
            report_datetime=timezone.now())
        self.assertEqual(self.requisition_meta_data_model.objects.filter(
            registered_subject=self.registered_subject).count(), 3)
        self.assertEqual(self.requisition_meta_data_model.objects.filter(
            entry_status=UNKEYED, registered_subject=self.registered_subject).count(), 3)

    def test_creates_requisition_meta_data2(self):
        """Meta data is unchanged if you re-save visit."""
        self.assertTrue(LabEntry.objects.all().count() > 0)
        self.subject_visit = SubjectVisit.objects.create(
            appointment=self.appointment,
            report_datetime=timezone.now())
        self.subject_visit.save()
        self.assertEqual(self.requisition_meta_data_model.objects.filter(
            entry_status=UNKEYED, registered_subject=self.registered_subject).count(), 3)

#     def test_updates_requisition_meta_data(self):
#         """Asserts metadata is updated if requisition model is keyed."""
#         self.assertEquals(self.requisition_meta_data_model.objects.filter(
#             registered_subject=self.appointment.registered_subject).count(), 0)
#         self.subject_visit = SubjectVisit.objects.create(
#             appointment=self.appointment,
#             report_datetime=timezone.now())
#         self.assertEquals(self.requisition_meta_data_model.objects.filter(
#             registered_subject=self.appointment.registered_subject,
#             entry_status=UNKEYED).count(), 3)
#         requisition_panel = self.requisition_meta_data_model.objects.filter(
#             registered_subject=self.registered_subject)[0].lab_entry.requisition_panel
#         panel = TestPanel.objects.get(name=requisition_panel.name)
#         aliquot_type = TestAliquotType.objects.get(alpha_code=requisition_panel.aliquot_type_alpha_code)
#         self.assertEqual(self.requisition_meta_data_model.objects.filter(
#             registered_subject=self.appointment.registered_subject,
#             entry_status=UNKEYED,
#             lab_entry__app_label='edc_testing',
#             lab_entry__model_name='testrequisition',
#             lab_entry__requisition_panel__name=panel.name).count(), 1)
#         obj = TestRequisitionFactory(
#             study_site=self.study_site,
#             subject_visit=self.subject_visit,
#             panel=panel,
#             aliquot_type=aliquot_type,
#             requisition_identifier='WJ000001')
# 
#         self.assertEqual(self.requisition_meta_data_model.objects.filter(
#             entry_status=KEYED,
#             registered_subject=self.registered_subject,
#             lab_entry__app_label='example',
#             lab_entry__model_name='testrequisition',
#             lab_entry__requisition_panel__name=obj.panel.name).count(), 1)

#     def test_updates_requisition_meta_data2(self):
#         """Meta data is set to KEYED and is unchanged if you re-save requisition or re-save visit."""
#         self.subject_visit = SubjectVisit.objects.create(
#             appointment=self.appointment,
#             report_datetime=timezone.now())
#         requisition_panel = self.requisition_meta_data_model.objects.filter(
#             registered_subject=self.registered_subject)[0].lab_entry.requisition_panel
#         panel = TestPanel.objects.get(name=requisition_panel.name)
#         aliquot_type = TestAliquotType.objects.get(alpha_code=requisition_panel.aliquot_type_alpha_code)
#         obj = TestRequisitionFactory(
#             study_site=self.study_site,
#             subject_visit=self.subject_visit,
#             panel=panel,
#             aliquot_type=aliquot_type,
#             requisition_identifier='WJ0000002')
#         obj.save()
#         self.assertEqual(self.requisition_meta_data_model.objects.filter(
#             entry_status=KEYED,
#             registered_subject=self.registered_subject,
#             lab_entry__app_label='example',
#             lab_entry__model_name='testrequisition',
#             lab_entry__requisition_panel__name=obj.panel.name).count(), 1)
#         self.subject_visit.save()
#         self.assertEqual(self.requisition_meta_data_model.objects.filter(
#             entry_status=KEYED,
#             registered_subject=self.registered_subject,
#             lab_entry__app_label='example',
#             lab_entry__model_name='testrequisition',
#             lab_entry__requisition_panel__name=obj.panel.name).count(), 1)
#         obj.save()
#         self.assertEqual(self.requisition_meta_data_model.objects.filter(
#             entry_status=KEYED,
#             registered_subject=self.registered_subject,
#             lab_entry__app_label='example',
#             lab_entry__model_name='testrequisition',
#             lab_entry__requisition_panel__name=obj.panel.name).count(), 1)
#
#     def test_updates_requisition_meta_data3(self):
#         """Meta data is set to KEYED and is unchanged if you re-save requisition or re-save visit."""
#         self.subject_visit = SubjectVisit.objects.create(
#             appointment=self.appointment,
#             report_datetime=timezone.now())
#         self.assertEqual(self.requisition_meta_data_model.objects.filter(registered_subject=self.registered_subject).count(), 3)
#         requisition_panel = self.requisition_meta_data_model.objects.filter(
#             registered_subject=self.registered_subject)[0].lab_entry.requisition_panel
#         panel = TestPanel.objects.get(name=requisition_panel.name)
#         aliquot_type = TestAliquotType.objects.get(alpha_code=requisition_panel.aliquot_type_alpha_code)
#         obj = TestRequisitionFactory(
#             study_site=self.study_site,
#             subject_visit=self.subject_visit,
#             panel=panel,
#             aliquot_type=aliquot_type,
#             requisition_identifier='WJ0000003')
#         obj.save()
#         self.assertEqual(self.requisition_meta_data_model.objects.filter(
#             entry_status=KEYED,
#             registered_subject=self.registered_subject,
#             lab_entry__app_label='example',
#             lab_entry__model_name='testrequisition',
#             lab_entry__requisition_panel__name=panel.name).count(), 1)
#         obj.delete()
#         self.assertEqual(self.requisition_meta_data_model.objects.filter(
#             entry_status=UNKEYED,
#             registered_subject=self.registered_subject,
#             lab_entry__app_label='example',
#             lab_entry__model_name='testrequisition',
#             lab_entry__requisition_panel__name=panel.name).count(), 1)

    def test_creates_meta_data2(self):
        """Meta data is created when visit tracking form is added, each instance set to NEW."""
        self.subject_visit = SubjectVisit.objects.create(
            appointment=self.appointment,
            report_datetime=timezone.now())
        self.assertEqual(
            self.crf_meta_data_model.objects.filter(
                entry_status=UNKEYED,
                registered_subject=self.registered_subject,
                crf_entry__app_label='example').count(), 3)

    def test_creates_meta_data3(self):
        """ """
        self.assertEqual(self.crf_meta_data_model.objects.filter(registered_subject=self.registered_subject).count(), 0)
        subject_visit = SubjectVisit.objects.create(
            appointment=self.appointment,
            report_datetime=timezone.now())
        self.assertEqual(self.crf_meta_data_model.objects.filter(registered_subject=self.registered_subject).count(), 3)
        CrfOne.objects.create(subject_visit=subject_visit)
        self.assertEqual(self.crf_meta_data_model.objects.filter(
            entry_status=KEYED, registered_subject=self.registered_subject).count(), 1)
        self.assertEqual(self.crf_meta_data_model.objects.filter(
            entry_status=UNKEYED, registered_subject=self.registered_subject).count(), 2)

    def test_creates_meta_data4(self):
        """Meta data is deleted when visit tracking form is deleted."""
        subject_visit = SubjectVisit.objects.create(
            appointment=self.appointment,
            report_datetime=timezone.now())
        self.assertEqual(self.requisition_meta_data_model.objects.filter(registered_subject=self.registered_subject).count(), 3)
        self.assertEqual(self.crf_meta_data_model.objects.filter(registered_subject=self.registered_subject).count(), 3)
        subject_visit.delete()
        self.assertEqual(self.crf_meta_data_model.objects.filter(registered_subject=self.registered_subject).count(), 0)
        self.assertEqual(self.requisition_meta_data_model.objects.filter(registered_subject=self.registered_subject).count(), 0)

    def test_creates_meta_data5(self):
        """Meta data is not created if visit reason is missed. See 'skip_create_visit_reasons class' attribute"""
        SubjectVisit.objects.create(
            appointment=self.appointment,
            report_datetime=timezone.now(),
            reason=MISSED_VISIT)
        self.assertEqual(
            self.crf_meta_data_model.objects.filter(registered_subject=self.registered_subject).count(), 0)

    def test_updates_meta_data4(self):
        """Meta data instance linked to the model is updated if model is entered."""
        self.subject_visit = SubjectVisit.objects.create(
            appointment=self.appointment,
            report_datetime=timezone.now())
        CrfOne.objects.create(subject_visit=self.subject_visit)
        self.assertEqual(self.crf_meta_data_model.objects.filter(
            entry_status=KEYED,
            registered_subject=self.registered_subject,
            crf_entry__app_label='example',
            crf_entry__model_name='testscheduledmodel1').count(), 1)

    def test_updates_meta_data5(self):
        """Meta data instance linked to the model is updated if model is entered and then updated."""
        self.subject_visit = SubjectVisit.objects.create(
            appointment=self.appointment,
            report_datetime=timezone.now())
        obj = CrfOne.objects.create(subject_visit=self.subject_visit)
        obj.save()
        self.assertEqual(self.crf_meta_data_model.objects.filter(
            entry_status=KEYED,
            registered_subject=self.registered_subject,
            crf_entry__app_label='example',
            crf_entry__model_name='testscheduledmodel1').count(), 1)

    def test_updates_meta_data6(self):
        """Meta data instance linked to the model is updated if model is deleted."""
        self.subject_visit = SubjectVisit.objects.create(
            appointment=self.appointment,
            report_datetime=timezone.now())
        self.assertEqual(self.crf_meta_data_model.objects.filter(
            entry_status=UNKEYED,
            registered_subject=self.registered_subject,
            crf_entry__app_label='example',
            crf_entry__model_name='testscheduledmodel1').count(), 1)
        obj = CrfOne.objects.create(subject_visit=self.subject_visit)
        self.assertEqual(self.crf_meta_data_model.objects.filter(
            entry_status=KEYED,
            registered_subject=self.registered_subject,
            crf_entry__app_label='example',
            crf_entry__model_name='testscheduledmodel1').count(), 1)
        obj.delete()
        self.assertEqual(self.crf_meta_data_model.objects.filter(
            entry_status=UNKEYED,
            registered_subject=self.registered_subject,
            crf_entry__app_label='example',
            crf_entry__model_name='testscheduledmodel1').count(), 1)

    def test_updates_meta_data7(self):
        """Meta data instance linked to the model is created if missing, knows model is KEYED."""
        self.subject_visit = SubjectVisit.objects.create(
            appointment=self.appointment,
            report_datetime=timezone.now())
        self.crf_meta_data_model.objects.filter(
            entry_status=UNKEYED,
            registered_subject=self.registered_subject,
            crf_entry__model_name='testscheduledmodel1').delete()
        CrfOne.objects.create(subject_visit=self.subject_visit)
        self.assertEqual(self.crf_meta_data_model.objects.filter(
            entry_status=KEYED,
            registered_subject=self.registered_subject,
            crf_entry__app_label='example',
            crf_entry__model_name='testscheduledmodel1').count(), 1)

#     def test_requisition_meta_data1(self):
#         """"""
#         self.subject_visit = SubjectVisit.objects.create(
#             appointment=self.appointment,
#             report_datetime=timezone.now())
#         self.assertEqual(
#             self.requisition_meta_data_model.objects.filter(registered_subject=self.registered_subject).count(), 3)
#         requisition_panels = [
#             requisition_meta_data.lab_entry.requisition_panel
#             for requisition_meta_data in self.requisition_meta_data_model.objects.filter(
#                 registered_subject=self.registered_subject)]
#         for requisition_panel in requisition_panels:
#             panel = TestPanel.objects.get(name=requisition_panel.name)
#             aliquot_type = TestAliquotType.objects.get(alpha_code=requisition_panel.aliquot_type_alpha_code)
#             obj = TestRequisitionFactory(
#                 study_site=self.study_site,
#                 subject_visit=self.subject_visit,
#                 panel=panel,
#                 aliquot_type=aliquot_type,
#                 requisition_identifier='WJ0000003')
#             obj.save()
#             self.assertEqual(self.requisition_meta_data_model.objects.filter(
#                 entry_status=KEYED,
#                 registered_subject=self.registered_subject,
#                 lab_entry__app_label='example',
#                 lab_entry__model_name='testrequisition',
#                 lab_entry__requisition_panel__name=panel.name).count(), 1)
#             self.assertEqual(self.requisition_meta_data_model.objects.filter(
#                 entry_status=UNKEYED,
#                 registered_subject=self.registered_subject).count(), 2)
#             self.assertEqual(self.requisition_meta_data_model.objects.filter(
#                 entry_status=KEYED,
#                 registered_subject=self.registered_subject).count(), 1)
#             obj.delete()
#             self.assertEqual(self.requisition_meta_data_model.objects.filter(
#                 entry_status=UNKEYED,
#                 registered_subject=self.registered_subject,
#                 lab_entry__app_label='example',
#                 lab_entry__model_name='testrequisition',
#                 lab_entry__requisition_panel__name=panel.name).count(), 1)
#             self.assertEqual(self.requisition_meta_data_model.objects.filter(
#                 entry_status=UNKEYED,
#                 registered_subject=self.registered_subject).count(), 3)

    def test_new_meta_data_never_keyed(self):
        """Meta data instance linked to the model is updated if model is deleted."""
        self.assertTrue(CrfOne.objects.all().count() == 0)
        self.assertEqual(self.crf_meta_data_model.objects.filter(registered_subject=self.registered_subject).count(), 0)
        self.subject_visit = SubjectVisit.objects.create(
            appointment=self.appointment,
            report_datetime=timezone.now())
        self.assertEqual(self.crf_meta_data_model.objects.filter(
            entry_status=KEYED, registered_subject=self.registered_subject).count(), 0)
