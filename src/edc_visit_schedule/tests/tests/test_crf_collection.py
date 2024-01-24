from django.test import TestCase

from edc_visit_schedule.visit import Crf, CrfCollection, FormsCollectionError


class TestCrfCollection(TestCase):
    def test_crf_collection_ok(self):
        crfs = [
            Crf(show_order=100, model="x.one"),
            Crf(show_order=200, model="x.two"),
            Crf(show_order=300, model="x.three"),
        ]
        try:
            CrfCollection(*crfs)
        except FormsCollectionError:
            self.fail("FormsCollectionError unexpectedly raised")

    def test_crf_collection_with_duplicate_ordering_raises(self):
        crfs = [
            Crf(show_order=100, model="x.one"),
            Crf(show_order=200, model="x.two"),
            Crf(show_order=100, model="x.three"),
        ]
        with self.assertRaises(FormsCollectionError) as cm:
            CrfCollection(*crfs)
        self.assertIn(
            'CrfCollection "show order" must be a unique sequence.',
            str(cm.exception),
        )
        self.assertIn("Duplicates [100].", str(cm.exception))

    def test_crf_collection_with_duplicate_models_raises(self):
        crfs = [
            Crf(show_order=100, model="x.one"),
            Crf(show_order=200, model="x.two"),
            Crf(show_order=300, model="x.one"),
        ]
        with self.assertRaises(FormsCollectionError) as cm:
            CrfCollection(*crfs)
        self.assertIn("Expected to be a unique sequence of crf/models.", str(cm.exception)),
        self.assertIn(" Duplicates ['x.one'].", str(cm.exception))
