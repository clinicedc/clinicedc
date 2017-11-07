from django.test import TestCase, tag

from ..visit import Crf, FormsCollection, FormsCollectionError


class TestFormsCollection(TestCase):

    def test_forms_collection_empty(self):
        crfs = []
        try:
            FormsCollection(*crfs)
        except FormsCollectionError as e:
            self.fail(f'FormsCollectionError unexpectedly raised. Got {e}')

    def test_forms_collection_none1(self):
        crfs = None
        try:
            FormsCollection(crfs)
        except FormsCollectionError as e:
            self.fail(f'FormsCollectionError unexpectedly raised. Got {e}')

    def test_forms_collection_order(self):
        crfs = []
        for i in range(0, 10):
            crfs.append(Crf(show_order=i, model='x.x'))
        try:
            FormsCollection(*crfs)
        except FormsCollectionError as e:
            self.fail(f'FormsCollectionError unexpectedly raised. Got {e}')
        crfs.append(0)
        self.assertRaises(FormsCollectionError, FormsCollection, *crfs)
