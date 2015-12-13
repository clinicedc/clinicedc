import factory

from collections import OrderedDict

from django.db import models
from django.test import TestCase
from django.utils import timezone

from edc_export.classes import ExportAsCsv
from edc_export.models import ExportHistory, ExportTransaction, ExportTrackingFieldsMixin


class TestExportModel(ExportTrackingFieldsMixin, models.Model):

    f1 = models.CharField(max_length=25, default='f1')
    f2 = models.CharField(max_length=25, default='f2')
    f3 = models.CharField(max_length=25, default='f3')
    f4 = models.CharField(max_length=25, default='f4')
    f5 = models.CharField(max_length=25, default='f5')
    subject_identifier = models.CharField(max_length=25)
    report_datetime = models.DateTimeField(default=timezone.now())

    class Meta:
        app_label = 'edc_export'


class Visit(models.Model):

    subject_identifier = models.CharField(max_length=10, default='1234567')

    report_datetime = models.DateTimeField(default=timezone.now)

    class Meta:
        app_label = 'edc_export'


class TestScheduledModel(ExportTrackingFieldsMixin, models.Model):

    visit = models.ForeignKey(Visit)
    f1 = models.CharField(max_length=25, default='f1')
    f2 = models.CharField(max_length=25, default='f2')
    f3 = models.CharField(max_length=25, default='f3')
    f4 = models.CharField(max_length=25, default='f4')
    f5 = models.CharField(max_length=25, default='f5')
    report_datetime = models.DateTimeField(default=timezone.now())

    class Meta:
        app_label = 'edc_export'


class TestExportModelFactory(factory.DjangoModelFactory):

    class Meta:
        model = TestExportModel


class TestScheduledModelFactory(factory.DjangoModelFactory):

    class Meta:
        model = TestScheduledModel


class TestExport(TestCase):

    def setUp(self):
        self.visit = Visit.objects.create()

    def test_reorder1(self):
        fields = ['f1', 'f2', 'f3', 'f4', 'f5']
        extra_fields = OrderedDict({'subject_identifier': 'subject_identifier',
                                    'report_datetime': 'report_datetime',
                                    'export_uuid': 'export_uuid',
                                    'export_datetime': 'export_datetime'})
        export_as_csv = ExportAsCsv([], model=TestExportModel, fields=fields, extra_fields=extra_fields)
        self.assertTrue(set(['f1', 'f2', 'f3', 'f4', 'f5']) < set(export_as_csv.field_names))

    def test_field_names1(self):
        """Correctly sets field names based on the given model."""
        for _ in range(0, 10):
            TestExportModelFactory()
        queryset = TestExportModel.objects.all()
        export_as_csv = ExportAsCsv(queryset, model=TestExportModel)
        export_as_csv.field_names.sort()
        field_names = [fld.name for fld in TestExportModel._meta.fields]
        field_names.sort()
        self.assertEqual(export_as_csv.field_names, field_names)

    def test_field_names2(self):
        """Extra fields are correctly updated to field names."""
        for _ in range(0, 10):
            TestExportModelFactory()
        queryset = TestExportModel.objects.all()
        extra_fields = OrderedDict({'field 10': 'f10', 'field 20': 'f20'})
        export_as_csv = ExportAsCsv(queryset, model=TestExportModel, extra_fields=extra_fields)
        export_as_csv.field_names.sort()
        field_names = [fld.name for fld in TestExportModel._meta.fields] + extra_fields.keys()
        field_names.sort()
        self.assertEqual(export_as_csv.field_names, field_names)

    def test_field_names3(self):
        """Fields in 'fields' attribute are correctly updated to field names."""
        for _ in range(0, 10):
            TestExportModelFactory()
        queryset = TestExportModel.objects.all()
        names = ['f10', 'f11']
        export_as_csv = ExportAsCsv(queryset, model=TestExportModel, fields=names)
        export_as_csv.field_names.sort()
        field_names = [fld.name for fld in TestExportModel._meta.fields] + names
        field_names.sort()
        self.assertEqual(export_as_csv.field_names, field_names)

    def test_field_names4(self):
        """Fields in 'exclude' attribute are correctly updated to field names."""
        for _ in range(0, 10):
            TestExportModelFactory()
        queryset = TestExportModel.objects.all()
        names = ['f1', 'f2']
        export_as_csv = ExportAsCsv(queryset, model=TestExportModel, exclude=names)
        export_as_csv.field_names.sort()
        field_names = [fld.name for fld in TestExportModel._meta.fields if fld.name not in names]
        field_names.sort()
        self.assertEqual(export_as_csv.field_names, field_names)

    def test_field_names_are_ordered(self):
        for _ in range(0, 10):
            TestExportModelFactory()
        queryset = TestExportModel.objects.all()
        names = ['hostname_created', 'f1', 'subject_identifier']
        export_as_csv = ExportAsCsv(queryset, model=TestExportModel, fields=names, show_all_fields=False)
        self.assertEqual(export_as_csv.field_names, ['subject_identifier', 'f1', 'hostname_created'])

    def test_header_row_is_ordered1(self):
        for _ in range(0, 10):
            TestExportModelFactory()
        queryset = TestExportModel.objects.all()
        names = ['f1', 'hostname_created', 'f2', 'subject_identifier']
        export_as_csv = ExportAsCsv(queryset, model=TestExportModel, fields=names, show_all_fields=False)
        self.assertEqual(export_as_csv.field_names, ['subject_identifier', 'f1', 'f2', 'hostname_created'])
        self.assertEqual(export_as_csv.header_row, ['subject_identifier', 'f1', 'f2', 'hostname_created'])

    def test_header_row_is_ordered2(self):
        for _ in range(0, 10):
            TestExportModelFactory()
        queryset = TestExportModel.objects.all()
        names = ['f1', 'hostname_created', 'f2', 'report_datetime', 'subject_identifier']
        export_as_csv = ExportAsCsv(queryset, model=TestExportModel, fields=names, show_all_fields=False)
        self.assertEqual(export_as_csv.field_names, ['subject_identifier', 'report_datetime', 'f1', 'f2', 'hostname_created'])
        self.assertEqual(export_as_csv.header_row, ['subject_identifier', 'report_datetime', 'f1', 'f2', 'hostname_created'])

    def test_header_row_is_ordered3(self):
        for _ in range(0, 10):
            TestExportModelFactory()
        queryset = TestExportModel.objects.all()
        names = ['f1', 'hostname_created', 'report_datetime', 'report_datetime', 'f2', 'subject_identifier', 'f3']
        export_as_csv = ExportAsCsv(queryset, model=TestExportModel, fields=names, show_all_fields=False)
        self.assertEqual(export_as_csv.field_names, ['subject_identifier', 'report_datetime', 'f1', 'f2', 'f3', 'hostname_created'])
        self.assertEqual(export_as_csv.header_row, ['subject_identifier', 'report_datetime', 'f1', 'f2', 'f3', 'hostname_created'])

    def test_getting_a_row1(self):
        for _ in range(0, 10):
            TestExportModelFactory()
        queryset = TestExportModel.objects.all()
        names = ['f1', 'hostname_created', 'report_datetime', 'report_datetime', 'f2', 'subject_identifier', 'f3']
        export_as_csv = ExportAsCsv(queryset, model=TestExportModel, fields=names, show_all_fields=False)
        export_as_csv.row_instance = TestExportModel.objects.all()[0]
        self.assertTrue(isinstance(export_as_csv.row, list))

    def test_getting_a_row2(self):
        """does it insert fields not directly on the model?"""
        test_scheduled_model = TestScheduledModelFactory(visit=self.visit)
        queryset = TestScheduledModel.objects.all()
        names = ['f1', 'hostname_created', 'report_datetime', 'report_datetime', 'f2', 'subject_identifier', 'f3']
        export_as_csv = ExportAsCsv(queryset, model=TestScheduledModel, fields=names, show_all_fields=False)
        export_as_csv.row_instance = test_scheduled_model
        self.assertTrue(isinstance(export_as_csv.row, list))

    def test_getting_a_row3(self):
        """does it insert fields not directly on the model? for example subject_identifier"""
        TestScheduledModelFactory(visit=self.visit)
        queryset = TestScheduledModel.objects.all()
        names = ['f1', 'hostname_created', 'report_datetime', 'report_datetime', 'f2', 'visit__appointment__registered_subject__subject_identifier', 'f3']
        export_as_csv = ExportAsCsv(queryset, model=TestScheduledModel, fields=names, show_all_fields=False)
        export_as_csv.row_instance = TestScheduledModel.objects.all()[0]
        self.assertNotIn('subject_identifier', export_as_csv.row)

    def test_getting_a_row4(self):
        """Assert unknown field name still gets in header but the row has no value"""
        TestScheduledModelFactory(visit=self.visit)
        queryset = TestScheduledModel.objects.all()
        fields = ['f1', 'hostname_created', 'report_datetime', 'report_datetime', 'f2', 'f3']
        extra_fields = {'bad_dog': 'visit__appointment__registered_subject__bad_dog'}
        export_as_csv = ExportAsCsv(queryset, model=TestScheduledModel, fields=fields, extra_fields=extra_fields, show_all_fields=False)
        export_as_csv.row_instance = TestScheduledModel.objects.all()[0]
        self.assertNotIn('bad_dog', export_as_csv.row)
        self.assertIn('bad_dog', export_as_csv.header_row)
        self.assertEqual(len(export_as_csv.row), len(export_as_csv.header_row))

    def test_getting_a_row5(self):
        """Assert known extra field name gets in header and the row has value"""
        test_scheduled_model = TestScheduledModelFactory(visit=self.visit)
        subject_identifier = test_scheduled_model.visit.appointment.registered_subject.subject_identifier
        queryset = TestScheduledModel.objects.all()
        fields = ['f1', 'hostname_created', 'report_datetime', 'report_datetime', 'f2', 'f3']
        extra_fields = OrderedDict({'subject_identifier': 'visit__appointment__registered_subject__subject_identifier'})
        export_as_csv = ExportAsCsv(queryset, model=TestScheduledModel, fields=fields, extra_fields=extra_fields, show_all_fields=False)
        export_as_csv.row_instance = TestScheduledModel.objects.all()[0]
        self.assertIn('subject_identifier', export_as_csv.header_row)
        self.assertIn(subject_identifier, export_as_csv.row)

    def test_updates_history1(self):
        """on edc_export, export_history is updated"""
        test_scheduled_model = TestScheduledModelFactory(visit=self.visit)
        queryset = TestScheduledModel.objects.all()
        fields = ['f1', 'hostname_created', 'report_datetime', 'report_datetime', 'f2', 'f3']
        extra_fields = OrderedDict({'subject_identifier': 'visit__appointment__registered_subject__subject_identifier'})
        export_as_csv = ExportAsCsv(queryset, model=TestScheduledModel, fields=fields, extra_fields=extra_fields, show_all_fields=False, track_history=True)
        export_as_csv.write_to_file()
        self.assertEqual(ExportHistory.objects.filter(instance_pk=test_scheduled_model.pk).count(), 1)

    def test_doesnt_update_history(self):
        """on edc_export, export_history is updated"""
        TestScheduledModelFactory(visit=self.visit)
        queryset = TestScheduledModel.objects.all()
        fields = ['f1', 'hostname_created', 'report_datetime', 'report_datetime', 'f2', 'f3']
        extra_fields = OrderedDict({'subject_identifier': 'visit__appointment__registered_subject__subject_identifier'})
        export_as_csv = ExportAsCsv(queryset, model=TestScheduledModel, fields=fields, extra_fields=extra_fields, show_all_fields=False, track_history=False)
        export_as_csv.write_to_file()
        self.assertEqual(ExportHistory.objects.all().count(), 0)

    def test_model_manager_serializes1(self):
        """test manager serializes to export_transactions, count"""
        TestScheduledModelFactory(visit=self.visit)
        self.assertEqual(ExportTransaction.objects.all().count(), 1)

    def test_model_manager_serializes2(self):
        """test manager serializes to export_transactions, look for pk"""
        test_scheduled_model = TestScheduledModelFactory(visit=self.visit)
        self.assertEqual(ExportTransaction.objects.get(tx_pk=test_scheduled_model.pk).tx_pk, test_scheduled_model.pk)

    def test_model_manager_serializes_on_insert(self):
        """test manager serializes and change_type is 'I'"""
        test_scheduled_model = TestScheduledModelFactory(visit=self.visit)
        self.assertEqual(ExportTransaction.objects.get(tx_pk=test_scheduled_model.pk).change_type, 'I')

    def test_model_manager_serializes_on_update(self):
        """test manager serializes and change_type is 'U'"""
        test_scheduled_model = TestScheduledModelFactory(visit=self.visit)
        test_scheduled_model.f1 = 'XXX'
        test_scheduled_model.save()
        self.assertEqual(ExportTransaction.objects.get(tx_pk=test_scheduled_model.pk, change_type='U').change_type, 'U')

    def test_model_manager_serializes_on_delete(self):
        """test manager serializes and change_type is 'D'"""
        test_scheduled_model = TestScheduledModelFactory(visit=self.visit)
        pk = test_scheduled_model.pk
        test_scheduled_model.delete()
        self.assertTrue(ExportTransaction.objects.get(tx_pk=pk, change_type='D').change_type, 'D')
