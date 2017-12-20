from django.test import TestCase, tag

from ..visit_schedule import ModelsCollection, ModelsCollectionError


class TestModelsCollection(TestCase):

    def test_update(self):
        models = ModelsCollection()
        models.update(subject_visit='edc_visit_schedule.subjectvisit')

    def test_get(self):
        models = ModelsCollection()
        models.update(subject_visit='edc_visit_schedule.subjectvisit')
        self.assertEqual(
            models.get('subject_visit'), 'edc_visit_schedule.subjectvisit')

    def test_attr(self):
        models = ModelsCollection()
        models.update(subject_visit='edc_visit_schedule.subjectvisit')
        self.assertEqual(
            models.subject_visit, 'edc_visit_schedule.subjectvisit')

    def test_onschedule_model(self):
        models = ModelsCollection()
        models.update(onschedule_model='edc_visit_schedule.onschedule')
        self.assertEqual(
            models.onschedule_model, 'edc_visit_schedule.onschedule')

    def test_offschedule_model(self):
        models = ModelsCollection()
        models.update(offschedule_model='edc_visit_schedule.onschedule')
        self.assertEqual(
            models.offschedule_model, 'edc_visit_schedule.onschedule')

    def test_validate(self):
        models = ModelsCollection()
        models.update(onschedule_model='edc_visit_schedule.onschedule')
        models.validate()

    def test_validate_bad(self):
        models = ModelsCollection()
        models.update(onschedule_model='edc_visit_schedule.blah')
        self.assertRaises(ModelsCollectionError, models.validate)
