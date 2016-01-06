from collections import OrderedDict

from edc_export.classes import ExportAsCsv
from edc_export.models import ExportHistory, ExportTransaction

from .base_test_case import BaseTestCase
from .test_models import TestCrfModel1


class TestExportAsCsv(BaseTestCase):

    def test_reorder1(self):
        fields = ['f1', 'f2', 'f3', 'f4', 'f5']
        extra_fields = OrderedDict(
            {'subject_identifier': 'subject_visit__appointment__registered_subject__subject_identifier',
             'report_datetime': 'report_datetime',
             'export_uuid': 'export_uuid',
             'export_datetime': 'export_datetime'})
        export_as_csv = ExportAsCsv([], model=TestCrfModel1, fields=fields, extra_fields=extra_fields)
        self.assertTrue(set(['f1', 'f2', 'f3', 'f4', 'f5']) < set(export_as_csv.field_names))

    def test_field_names1(self):
        """Correctly sets field names based on the given model."""
        test_crf_model1 = TestCrfModel1.objects.create(test_visit_model1=self.test_visit_model1)
        for _ in range(0, 10):
            test_crf_model1.save()
        queryset = TestCrfModel1.objects.all()
        export_as_csv = ExportAsCsv(queryset, model=TestCrfModel1)
        export_as_csv.field_names.sort()
        field_names = [fld.name for fld in TestCrfModel1._meta.fields]
        field_names.sort()
        self.assertEqual(export_as_csv.field_names, field_names)

    def test_field_names2(self):
        """Extra fields are correctly updated to field names."""
        test_crf_model1 = TestCrfModel1.objects.create(test_visit_model1=self.test_visit_model1)
        for _ in range(0, 10):
            test_crf_model1.save()
        queryset = TestCrfModel1.objects.all()
        extra_fields = OrderedDict({'field 10': 'f10', 'field 20': 'f20'})
        export_as_csv = ExportAsCsv(queryset, model=TestCrfModel1, extra_fields=extra_fields)
        export_as_csv.field_names.sort()
        field_names = [fld.name for fld in TestCrfModel1._meta.fields] + extra_fields.keys()
        field_names.sort()
        self.assertEqual(export_as_csv.field_names, field_names)

    def test_field_names3(self):
        """Fields in 'fields' attribute are correctly updated to field names."""
        test_crf_model1 = TestCrfModel1.objects.create(test_visit_model1=self.test_visit_model1)
        for _ in range(0, 10):
            test_crf_model1.save()
        queryset = TestCrfModel1.objects.all()
        names = ['f10', 'f11']
        export_as_csv = ExportAsCsv(queryset, model=TestCrfModel1, fields=names)
        export_as_csv.field_names.sort()
        field_names = [fld.name for fld in TestCrfModel1._meta.fields] + names
        field_names.sort()
        self.assertEqual(export_as_csv.field_names, field_names)

    def test_field_names4(self):
        """Fields in 'exclude' attribute are correctly updated to field names."""
        test_crf_model1 = TestCrfModel1.objects.create(test_visit_model1=self.test_visit_model1)
        for _ in range(0, 10):
            test_crf_model1.save()
        queryset = TestCrfModel1.objects.all()
        names = ['f1', 'f2']
        export_as_csv = ExportAsCsv(queryset, model=TestCrfModel1, exclude=names)
        export_as_csv.field_names.sort()
        field_names = [fld.name for fld in TestCrfModel1._meta.fields if fld.name not in names]
        field_names.sort()
        self.assertEqual(export_as_csv.field_names, field_names)

    def test_field_names_are_ordered(self):
        test_crf_model1 = TestCrfModel1.objects.create(test_visit_model1=self.test_visit_model1)
        for _ in range(0, 10):
            test_crf_model1.save()
        queryset = TestCrfModel1.objects.all()
        names = ['hostname_created', 'f1', 'subject_identifier']
        export_as_csv = ExportAsCsv(queryset, model=TestCrfModel1, fields=names, show_all_fields=False)
        self.assertEqual(export_as_csv.field_names, ['subject_identifier', 'f1', 'hostname_created'])

    def test_header_row_is_ordered1(self):
        test_crf_model1 = TestCrfModel1.objects.create(test_visit_model1=self.test_visit_model1)
        for _ in range(0, 10):
            test_crf_model1.save()
        queryset = TestCrfModel1.objects.all()
        names = ['f1', 'hostname_created', 'f2', 'subject_identifier']
        export_as_csv = ExportAsCsv(queryset, model=TestCrfModel1, fields=names, show_all_fields=False)
        self.assertEqual(export_as_csv.field_names, ['subject_identifier', 'f1', 'f2', 'hostname_created'])
        self.assertEqual(export_as_csv.header_row, ['subject_identifier', 'f1', 'f2', 'hostname_created'])

    def test_header_row_is_ordered2(self):
        test_crf_model1 = TestCrfModel1.objects.create(test_visit_model1=self.test_visit_model1)
        for _ in range(0, 10):
            test_crf_model1.save()
        queryset = TestCrfModel1.objects.all()
        names = ['f1', 'hostname_created', 'f2', 'report_datetime', 'subject_identifier']
        export_as_csv = ExportAsCsv(queryset, model=TestCrfModel1, fields=names, show_all_fields=False)
        self.assertEqual(
            export_as_csv.field_names,
            ['subject_identifier', 'report_datetime', 'f1', 'f2', 'hostname_created'])
        self.assertEqual(
            export_as_csv.header_row,
            ['subject_identifier', 'report_datetime', 'f1', 'f2', 'hostname_created'])

    def test_header_row_is_ordered3(self):
        test_crf_model1 = TestCrfModel1.objects.create(test_visit_model1=self.test_visit_model1)
        for _ in range(0, 10):
            test_crf_model1.save()
        queryset = TestCrfModel1.objects.all()
        names = ['f1', 'hostname_created', 'report_datetime', 'report_datetime', 'f2', 'subject_identifier', 'f3']
        export_as_csv = ExportAsCsv(queryset, model=TestCrfModel1, fields=names, show_all_fields=False)
        self.assertEqual(
            export_as_csv.field_names,
            ['subject_identifier', 'report_datetime', 'f1', 'f2', 'f3', 'hostname_created'])
        self.assertEqual(
            export_as_csv.header_row,
            ['subject_identifier', 'report_datetime', 'f1', 'f2', 'f3', 'hostname_created'])

    def test_getting_a_row1(self):
        test_crf_model1 = TestCrfModel1.objects.create(test_visit_model1=self.test_visit_model1)
        for _ in range(0, 10):
            test_crf_model1.save()
        queryset = TestCrfModel1.objects.all()
        names = ['f1', 'hostname_created', 'report_datetime', 'report_datetime', 'f2', 'subject_identifier', 'f3']
        export_as_csv = ExportAsCsv(queryset, model=TestCrfModel1, fields=names, show_all_fields=False)
        export_as_csv.row_instance = TestCrfModel1.objects.all()[0]
        self.assertTrue(isinstance(export_as_csv.fetch_row(), list))

    def test_getting_a_row2(self):
        """does it insert fields not directly on the model?"""
        test_crf_model = TestCrfModel1.objects.create(test_visit_model1=self.test_visit_model1)
        queryset = TestCrfModel1.objects.all()
        names = ['f1', 'hostname_created', 'report_datetime', 'report_datetime', 'f2', 'subject_identifier', 'f3']
        export_as_csv = ExportAsCsv(queryset, model=TestCrfModel1, fields=names, show_all_fields=False)
        export_as_csv.row_instance = test_crf_model
        self.assertTrue(isinstance(export_as_csv.fetch_row(), list))

    def test_getting_a_row3(self):
        """does it insert fields not directly on the model? for example subject_identifier"""
        TestCrfModel1.objects.create(test_visit_model1=self.test_visit_model1)
        queryset = TestCrfModel1.objects.all()
        names = ['f1', 'hostname_created', 'report_datetime',
                 'report_datetime', 'f2',
                 'test_visit_model1__appointment__registered_subject__subject_identifier', 'f3']
        export_as_csv = ExportAsCsv(queryset, model=TestCrfModel1, fields=names, show_all_fields=False)
        export_as_csv.row_instance = TestCrfModel1.objects.all()[0]
        self.assertNotIn('subject_identifier', export_as_csv.fetch_row())

    def test_getting_a_row4(self):
        """Assert unknown field name still gets in header but the row has no value"""
        TestCrfModel1.objects.create(test_visit_model1=self.test_visit_model1)
        queryset = TestCrfModel1.objects.all()
        fields = ['f1', 'hostname_created', 'report_datetime', 'report_datetime', 'f2', 'f3']
        extra_fields = {'bad_dog': 'test_visit_model1__appointment__registered_subject__bad_dog'}
        export_as_csv = ExportAsCsv(
            queryset, model=TestCrfModel1, fields=fields, extra_fields=extra_fields, show_all_fields=False)
        export_as_csv.row_instance = TestCrfModel1.objects.all()[0]
        self.assertNotIn('bad_dog', export_as_csv.fetch_row())
        self.assertIn('bad_dog', export_as_csv.header_row)
        self.assertEqual(len(export_as_csv.fetch_row()), len(export_as_csv.header_row))

    def test_getting_a_row5(self):
        """Assert known extra field name gets in header and the row has value"""
        test_crf_model = TestCrfModel1.objects.create(test_visit_model1=self.test_visit_model1)
        subject_identifier = test_crf_model.test_visit_model1.appointment.registered_subject.subject_identifier
        queryset = TestCrfModel1.objects.all()
        fields = ['f1', 'hostname_created', 'report_datetime', 'report_datetime', 'f2', 'f3']
        extra_fields = OrderedDict(
            {'subject_identifier': 'test_visit_model1__appointment__registered_subject__subject_identifier'})
        export_as_csv = ExportAsCsv(
            queryset, model=TestCrfModel1, fields=fields, extra_fields=extra_fields, show_all_fields=False)
        export_as_csv.row_instance = TestCrfModel1.objects.all()[0]
        self.assertIn('subject_identifier', export_as_csv.header_row)
        self.assertIn(subject_identifier, export_as_csv.fetch_row())

    def test_updates_history1(self):
        """on export, export_history is updated"""
        test_crf_model = TestCrfModel1.objects.create(test_visit_model1=self.test_visit_model1)
        queryset = TestCrfModel1.objects.all()
        fields = ['f1', 'hostname_created', 'report_datetime', 'report_datetime', 'f2', 'f3']
        extra_fields = OrderedDict(
            {'subject_identifier': 'test_visit_model1__appointment__registered_subject__subject_identifier'})
        export_as_csv = ExportAsCsv(
            queryset, model=TestCrfModel1, fields=fields,
            extra_fields=extra_fields, show_all_fields=False, track_history=True)
        export_as_csv.write_to_file()
        self.assertEqual(ExportHistory.objects.filter(pk_list__contains=test_crf_model.pk).count(), 1)

    def test_doesnt_update_history(self):
        """on export, export_history is updated"""
        TestCrfModel1.objects.create(test_visit_model1=self.test_visit_model1)
        queryset = TestCrfModel1.objects.all()
        fields = ['f1', 'hostname_created', 'report_datetime', 'report_datetime', 'f2', 'f3']
        extra_fields = OrderedDict(
            {'subject_identifier': 'test_visit_model1__appointment__registered_subject__subject_identifier'})
        export_as_csv = ExportAsCsv(
            queryset, model=TestCrfModel1, fields=fields,
            extra_fields=extra_fields, show_all_fields=False, track_history=False)
        export_as_csv.write_to_file()
        self.assertEqual(ExportHistory.objects.all().count(), 0)

    def test_model_manager_serializes1(self):
        """test manager serializes to export_transactions, count"""
        TestCrfModel1.objects.create(test_visit_model1=self.test_visit_model1)
        self.assertEqual(ExportTransaction.objects.all().count(), 1)

    def test_model_manager_serializes2(self):
        """test manager serializes to export_transactions, look for pk"""
        test_crf_model = TestCrfModel1.objects.create(test_visit_model1=self.test_visit_model1)
        self.assertEqual(
            ExportTransaction.objects.get(tx_pk=test_crf_model.pk).tx_pk, test_crf_model.pk)

    def test_model_manager_serializes_on_insert(self):
        """test manager serializes and export_change_type is 'I'"""
        test_crf_model = TestCrfModel1.objects.create(test_visit_model1=self.test_visit_model1)
        self.assertEqual(ExportTransaction.objects.get(tx_pk=test_crf_model.pk).export_change_type, 'I')

    def test_model_manager_serializes_on_update(self):
        """test manager serializes and export_change_type is 'U'"""
        test_crf_model = TestCrfModel1.objects.create(test_visit_model1=self.test_visit_model1)
        test_crf_model.f1 = 'XXX'
        test_crf_model.save()
        self.assertEqual(
            ExportTransaction.objects.get(tx_pk=test_crf_model.pk, export_change_type='U').export_change_type, 'U')

    def test_model_manager_serializes_on_delete(self):
        """test manager serializes and export_change_type is 'D'"""
        test_crf_model = TestCrfModel1.objects.create(test_visit_model1=self.test_visit_model1)
        pk = test_crf_model.pk
        test_crf_model.delete()
        self.assertTrue(
            ExportTransaction.objects.get(tx_pk=pk, export_change_type='D').export_change_type, 'D')
