from django import forms
from django.test import TestCase, tag
from edc_base.sites.utils import add_or_update_django_sites
from edc_constants.constants import OTHER, YES, NO, NOT_APPLICABLE

from ..forms import BoxForm, ManifestForm, BoxTypeForm, RequisitionFormMixin
from ..models import Aliquot
from .models import SubjectRequisition, SimpleSubjectVisit as SubjectVisit
from .site_labs_test_helper import SiteLabsTestHelper


class TestForms(TestCase):

    @classmethod
    def setUpClass(cls):
        add_or_update_django_sites(
            sites=((10, 'test_site', 'Test Site'), ), fqdn='clinicedc.org')
        return super().setUpClass()

    def tearDown(self):
        super().tearDown()

    def test_box_form_specimen_types1(self):
        data = {'specimen_types': '12, 13'}
        form = BoxForm(data=data)
        form.is_valid()
        self.assertNotIn('specimen_types', list(form.errors.keys()))

    def test_box_form_specimen_types2(self):
        data = {'specimen_types': None}
        form = BoxForm(data=data)
        form.is_valid()
        self.assertIn('specimen_types', list(form.errors.keys()))

    def test_box_form_specimen_types3(self):
        data = {'specimen_types': 'AA, BB'}
        form = BoxForm(data=data)
        form.is_valid()
        self.assertIn('specimen_types', list(form.errors.keys()))

    def test_box_form_specimen_types4(self):
        data = {'specimen_types': '12, 13, AA'}
        form = BoxForm(data=data)
        form.is_valid()
        self.assertIn('specimen_types', list(form.errors.keys()))

    def test_box_form_specimen_types5(self):
        data = {'specimen_types': '12, 13, 13'}
        form = BoxForm(data=data)
        form.is_valid()
        self.assertIn('specimen_types', list(form.errors.keys()))

    def test_box_type_form1(self):
        data = {'across': 5, 'down': 6, 'total': 30}
        form = BoxTypeForm(data=data)
        form.is_valid()
        self.assertNotIn('total', list(form.errors.keys()))

    def test_box_type_form2(self):
        data = {'across': 5, 'down': 6, 'total': 10}
        form = BoxTypeForm(data=data)
        form.is_valid()
        self.assertIn('total', list(form.errors.keys()))

    def test_manifest_form1(self):
        data = {'category': OTHER, 'category_other': None}
        form = ManifestForm(data=data)
        form.is_valid()
        self.assertIn('category_other', list(form.errors.keys()))

    def test_manifest_form2(self):
        data = {'category': 'blah', 'category_other': None}
        form = ManifestForm(data=data)
        form.is_valid()
        self.assertNotIn('category_other', list(form.errors.keys()))

    def test_requisition_form(self):
        class RequisitionForm(RequisitionFormMixin, forms.ModelForm):
            class Meta:
                fields = '__all__'
                model = SubjectRequisition

        data = {'is_drawn': YES, 'reason_not_drawn': NOT_APPLICABLE}
        form = RequisitionForm(data=data)
        form.is_valid()
        self.assertNotIn('reason_not_drawn', list(form.errors.keys()))

        data = {
            'is_drawn': NO,
            'reason_not_drawn': 'collection_failed',
            'item_type': NOT_APPLICABLE}
        form = RequisitionForm(data=data)
        form.is_valid()
        self.assertNotIn('reason_not_drawn', list(form.errors.keys()))
        self.assertNotIn('drawn_datetime', list(form.errors.keys()))
        self.assertNotIn('item_type', list(form.errors.keys()))


class TestForms2(TestCase):

    lab_helper = SiteLabsTestHelper()

    def setUp(self):
        self.lab_helper.setup_site_labs()

        class RequisitionForm(RequisitionFormMixin, forms.ModelForm):
            aliquot_model = Aliquot

            class Meta:
                fields = '__all__'
                model = SubjectRequisition
        self.form_cls = RequisitionForm
        self.subject_visit = SubjectVisit.objects.create()

    def test_requisition_form_packed_cannot_change(self):
        obj = SubjectRequisition.objects.create(
            subject_visit=self.subject_visit,
            panel=self.lab_helper.panel.panel_model_obj,
            packed=True,
            processed=True,
            received=True)
        data = {'packed': False, 'processed': True, 'received': True}
        form = self.form_cls(data=data, instance=obj)
        form.is_valid()
        self.assertIn('packed', list(form.errors.keys()))

    def test_requisition_form_processed_can_change_if_no_aliquots(self):
        obj = SubjectRequisition.objects.create(
            subject_visit=self.subject_visit,
            panel=self.lab_helper.panel.panel_model_obj,
            packed=True,
            processed=True,
            received=True)
        data = {'packed': True, 'processed': False, 'received': True}
        form = self.form_cls(data=data, instance=obj)
        form.is_valid()
        self.assertNotIn('processed', list(form.errors.keys()))

    def test_requisition_form_processed_cannot_change_if_aliquots(self):
        obj = SubjectRequisition.objects.create(
            subject_visit=self.subject_visit,
            panel=self.lab_helper.panel.panel_model_obj,
            packed=True,
            processed=True,
            received=True)
        Aliquot.objects.create(
            aliquot_identifier='1111',
            requisition_identifier=obj.requisition_identifier,
            count=1)
        data = {'packed': True, 'processed': False, 'received': True}
        form = self.form_cls(data=data, instance=obj)
        form.is_valid()
        self.assertIn('processed', list(form.errors.keys()))

    def test_requisition_form_received_cannot_change(self):
        obj = SubjectRequisition.objects.create(
            subject_visit=self.subject_visit,
            panel=self.lab_helper.panel.panel_model_obj,
            packed=True,
            processed=True,
            received=True)
        data = {'packed': True, 'processed': True, 'received': False}
        form = self.form_cls(data=data, instance=obj)
        form.is_valid()
        self.assertIn('received', list(form.errors.keys()))

    def test_requisition_form_received_cannot_be_set_by_form(self):
        obj = SubjectRequisition.objects.create(
            subject_visit=self.subject_visit,
            panel=self.lab_helper.panel.panel_model_obj,
            received=False)
        data = {'received': True}
        form = self.form_cls(data=data, instance=obj)
        form.is_valid()
        self.assertIn('received', list(form.errors.keys()))

    def test_requisition_form_cannot_be_changed_if_received(self):
        obj = SubjectRequisition.objects.create(
            subject_visit=self.subject_visit,
            panel=self.lab_helper.panel.panel_model_obj,
            received=True)
        data = {'received': True}
        form = self.form_cls(data=data, instance=obj)
        form.is_valid()
        self.assertIn('Requisition may not be changed',
                      ''.join(form.errors.get('__all__')))
