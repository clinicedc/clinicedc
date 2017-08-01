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

    def test_enrollment_model(self):
        models = ModelsCollection()
        models.update(enrollment_model='edc_visit_schedule.enrollment')
        self.assertEqual(
            models.enrollment_model, 'edc_visit_schedule.enrollment')

    def test_disenrollment_model(self):
        models = ModelsCollection()
        models.update(disenrollment_model='edc_visit_schedule.enrollment')
        self.assertEqual(
            models.disenrollment_model, 'edc_visit_schedule.enrollment')

    def test_validate(self):
        models = ModelsCollection()
        models.update(enrollment_model='edc_visit_schedule.enrollment')
        models.validate()

    def test_validate_bad(self):
        models = ModelsCollection()
        models.update(enrollment_model='edc_visit_schedule.blah')
        self.assertRaises(ModelsCollectionError, models.validate)
