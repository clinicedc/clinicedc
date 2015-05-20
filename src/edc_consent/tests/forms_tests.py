from django.test import TestCase
from edc.subject.registration.models import RegisteredSubject
from edc.testing.forms import TestSubjectUuidModelForm
from edc.testing.tests.factories import TestM2mFactory, TestForeignKeyFactory
from .base_methods import BaseMethods


class FormsTests(TestCase, BaseMethods):

    def setUp(self):
        from edc.testing.tests.factories import TestConsentFactory
        self.test_consent_factory = TestConsentFactory
        self.create_study_variables()

    def test_base_consented_model_form(self):
        subject_consent = self.test_consent_factory()
        self.prepare_consent_catalogue()
        registered_subject = RegisteredSubject.objects.get(subject_identifier=subject_consent.subject_identifier)
        test_m2m = TestM2mFactory(name='test_m2m', short_name='test_m2m')
        test_fk = TestForeignKeyFactory(name='test_fk', short_name='test_fk')

        form_data = {'name': 'TEST',
                     'registered_subject': registered_subject.pk,
                     'test_foreign_key': test_fk.pk,
                     'test_many_to_many': test_m2m}
        form = TestSubjectUuidModelForm(data=form_data)
        form.full_clean()
        self.assertFalse(form.is_valid())
