from datetime import datetime

from django.test import TestCase

from edc.subject.registration.models import RegisteredSubject

from edc_consent import BaseConsentHistory


class ConsentUpdateTests(TestCase):

    def setUp(self):
        from edc.testing.tests.factories import TestConsentFactory
        self.test_consent_factory = TestConsentFactory
        self.create_study_variables()

    def test_p1(self):
        print 'create a edc_consent'
        self.test_consent_factory(first_name='THING1')
        self.test_consent_factory(first_name='THING2')
        self.test_consent_factory(first_name='THING3')
        test_consent = self.test_consent_factory(first_name='THING4')
        print 'assert has edc_consent history methods'
        self.assertTrue('get_consent_history_model' in dir(test_consent))
        self.assertTrue('update_consent_history' in dir(test_consent))
        self.assertTrue('delete_consent_history' in dir(test_consent))
        print 'confirm RS created'
        self.assertEquals(RegisteredSubject.objects.all().count(), 4)
        self.assertEquals(RegisteredSubject.objects.filter(first_name=test_consent.first_name, dob=test_consent.dob, initials=test_consent.initials).count(), 1)
        print 'assert get_consent_history_model returns a model of base class BaseConsentHistory'
        history_model = test_consent.get_consent_history_model()
        self.assertTrue(issubclass(test_consent.get_consent_history_model(), BaseConsentHistory))
        print 'assert edc_consent history now includes edc_consent for {0}'.format(test_consent)
        self.assertEquals(history_model.objects.filter(registered_subject=test_consent.registered_subject).count(), 1)
        test_consent_history = history_model.objects.get(registered_subject=test_consent.registered_subject, consent_pk=test_consent.pk)
        self.assertEqual(test_consent.consent_datetime, test_consent_history.consent_datetime)
        print 'update edc_consent for {0}'.format(test_consent)
        test_consent.consent_datetime = datetime.today()
        test_consent.save()
        print 'assert history updated for {0}'.format(test_consent)
        test_consent_history = history_model.objects.get(registered_subject=test_consent.registered_subject, consent_pk=test_consent.pk)
        self.assertEqual(test_consent.consent_datetime, test_consent_history.consent_datetime)
        print 'delete edc_consent for {0}'.format(test_consent)
        test_consent.delete()
        print 'assert history update for {0}'.format(test_consent)
        self.assertEqual(history_model.objects.filter(registered_subject=test_consent.registered_subject, consent_pk=test_consent.pk).count(), 0)
        self.assertEqual(history_model.objects.all().count(), 3)
