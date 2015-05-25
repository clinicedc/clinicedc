# from django.test import TestCase
# from edc.core.bhp_variables.tests.factories import StudySiteFactory, StudySpecificFactory
# from edc.subject.registration.models import RegisteredSubject
# 
# 
# class ModelTests(TestCase):
# 
#     def setUp(self):
#         from edc.testing.tests.factories import TestConsentFactory
#         self.test_consent_factory = TestConsentFactory
#         self.create_study_variables()
# 
#     def test_p2(self):
#         """TEST registered subject is create when edc_consent is created"""
# 
#         study_site = StudySiteFactory(site_code='10', site_name='TEST_SITE')
#         StudySpecificFactory()
#         print "create a new edc_consent"
#         subject_consent = self.test_consent_factory(first_name='ERIK1', study_site=study_site)
#         print 'assert subject_identifier is not None. Got {0}'.format(subject_consent.subject_identifier)
#         self.assertIsNotNone(subject_consent.subject_identifier)
#         # confirm registered_subject is created and updated
#         print 'get the registered subject created by the bhp_subject signal.'
#         registered_subject = RegisteredSubject.objects.get(subject_identifier=subject_consent.subject_identifier)
#         print 'assert has same subject identifier'
#         self.assertEqual(registered_subject.subject_identifier, subject_consent.subject_identifier)
#         print 'assert has same first name'
#         self.assertEqual(registered_subject.first_name, subject_consent.first_name)
#         print "update subject edc_consent, change first name"
#         subject_consent.first_name = 'ERIK2'
#         subject_consent.save()
#         print "confirm registered subject is updated with new first name"
#         registered_subject = RegisteredSubject.objects.get(subject_identifier=subject_consent.subject_identifier)
#         self.assertEqual(registered_subject.first_name, 'ERIK2')
