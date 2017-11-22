from django.test import TestCase, tag
from edc_pdutils.dialects.crf_dialect import CrfDialect


class DummyDfHandler:
    visit_tbl = 'edc_pdutils_subjectvisit'
    appointment_tbl = 'edc_appointment_appointment'
    registered_subject_tbl = 'edc_registration_registeredsubject'

    def __init__(self, visit_column=None):
        self.visit_column = visit_column or 'subject_visit_id'


class TestDialects(TestCase):

    def test_init(self):
        obj = DummyDfHandler()
        crf_dialect = CrfDialect(obj=obj)
        self.assertTrue(
            crf_dialect.select_visit_and_related)
        self.assertIn(
            'SELECT',
            crf_dialect.select_visit_and_related[0])
        self.assertIn(
            obj.visit_column,
            crf_dialect.select_visit_and_related[0])
        self.assertIn(
            obj.appointment_tbl,
            crf_dialect.select_visit_and_related[0])
        self.assertIn(
            obj.registered_subject_tbl,
            crf_dialect.select_visit_and_related[0])
        self.assertIn(
            obj.visit_tbl,
            crf_dialect.select_visit_and_related[0])

    def test_uses_df_handlers_visit_column(self):
        obj = DummyDfHandler(visit_column='erik_visit_id')
        crf_dialect = CrfDialect(obj=obj)
        self.assertTrue(
            crf_dialect.select_visit_and_related)
        self.assertIn(
            'SELECT',
            crf_dialect.select_visit_and_related[0])
        self.assertIn(
            obj.visit_column,
            crf_dialect.select_visit_and_related[0])
