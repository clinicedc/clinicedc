from django.test import TestCase, tag

from ..visit import Crf, FormsCollection, FormsCollectionError
from django.test.utils import override_settings


class TestFormsCollection(TestCase):
    def test_forms_collection_empty(self):
        crfs = []
        try:
            FormsCollection(*crfs)
        except FormsCollectionError as e:
            self.fail(f"FormsCollectionError unexpectedly raised. Got {e}")

    def test_forms_collection_none1(self):
        crfs = None
        try:
            FormsCollection(crfs)
        except FormsCollectionError as e:
            self.fail(f"FormsCollectionError unexpectedly raised. Got {e}")

    def test_forms_collection_order(self):
        crfs = []
        for i in range(0, 10):
            crfs.append(Crf(show_order=i, model="x.x"))
        try:
            FormsCollection(*crfs)
        except FormsCollectionError as e:
            self.fail(f"FormsCollectionError unexpectedly raised. Got {e}")
        crfs.append(Crf(show_order=0, model="x.x"))
        self.assertRaises(FormsCollectionError, FormsCollection, *crfs)

    @override_settings(SITE_ID=40)
    def test_forms_collection_excludes_by_site_id(self):
        crfs = []
        for i in range(0, 5):
            crfs.append(Crf(show_order=i, model=f"x.{i}"))
        for i in range(6, 11):
            crfs.append(Crf(show_order=i, model=f"x.{i}", site_ids=[10]))
        forms = FormsCollection(*crfs)
        self.assertEqual(len(forms.forms), 5)

    @override_settings(SITE_ID=40)
    def test_forms_collection_excludes_by_site_id2(self):
        crfs = []
        for i in range(0, 5):
            crfs.append(Crf(show_order=i, model=f"x.{i}"))
        for i in range(6, 11):
            crfs.append(Crf(show_order=i, model=f"x.{i}", site_ids=[40]))
        forms = FormsCollection(*crfs)
        self.assertEqual(len(forms.forms), 10)

    @override_settings(SITE_ID=40)
    def test_forms_collection_excludes_by_site_id3(self):
        crfs = []
        for i in range(0, 5):
            crfs.append(Crf(show_order=i, model=f"x.{i}"))
        for i in range(6, 11):
            crfs.append(Crf(show_order=i, model=f"x.{i}"))
        forms = FormsCollection(*crfs)
        self.assertEqual(len(forms.forms), 10)
