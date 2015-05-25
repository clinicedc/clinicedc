import re

from django.test import TestCase
from django.conf import settings

from edc.core.identifier.exceptions import IdentifierError
from edc.testing.models import TestConsent

from ..models import RegisteredSubject

from .factories import RegisteredSubjectFactory


class ModelTests(TestCase):

    def setUp(self):
        from edc.testing.tests.factories import TestConsentFactory
        self.test_consent_factory = TestConsentFactory
        self.create_study_variables()

    def test_p1(self):
        """Tests the subject_identifier is a uuid by default"""
        print('test subject_identifier is uuid by default')
        registered_subject = RegisteredSubjectFactory()
        re_pk = re.compile('[\w]{8}-[\w]{4}-[\w]{4}-[\w]{4}-[\w]{12}')
        self.assertTrue(re_pk.match(registered_subject.subject_identifier))

    def test_p2(self):
        """Tests natural key."""

        re_pk = re.compile('[\w]{8}-[\w]{4}-[\w]{4}-[\w]{4}-[\w]{12}')
        for index, cls_tpl in enumerate([(RegisteredSubject, RegisteredSubjectFactory), (TestConsent, self.test_consent_factory)]):
            cls, cls_factory = cls_tpl
            print('using {0}'.format(cls._meta.object_name))
            print('test {0} natural key'.format(cls._meta.object_name))
            rs = cls_factory()
            rs2 = cls.objects.get_by_natural_key(rs.subject_identifier_as_pk)
            self.assertEqual(rs, rs2)
            args = rs.natural_key()
            rs3 = cls.objects.get_by_natural_key(*args)
            self.assertEqual(rs, rs3)
            print('test {0} does not change subject identifier on save of existing instance'.format(cls._meta.object_name))
            rs = cls_factory()
            old_identifier = rs.subject_identifier
            rs.subject_identifier = 'TEST_IDENTIFIER{0}'.format(index)
            if issubclass(cls, RegisteredSubject):
                # should not raise an error if identifier is changed as this is what the consent model will do
                # on save.
                # see model method check_if_may_change_subject_identifier(self, using)
                self.assertIsNone(rs.save())
                rs = cls.objects.get(pk=rs.pk)
                self.assertNotEqual(old_identifier, rs.subject_identifier)
                # put the identifier back for tests below (should not be allowed to do this if consented???)
                rs.subject_identifier = old_identifier
                rs.save()
            else:
                self.assertRaises(IdentifierError, rs.save)
                rs = cls.objects.get(pk=rs.pk)
                self.assertEqual(old_identifier, rs.subject_identifier)
            if rs.get_user_provided_subject_identifier_attrname():
                print('test {0} uses user provided subject identifier'.format(cls._meta.object_name))
                rs = cls_factory(**{rs.get_user_provided_subject_identifier_attrname(): 'TEST_IDENTIFIER_USER{0}'.format(index)})
                rs = cls.objects.get(pk=rs.pk)
                self.assertEqual(rs.subject_identifier, 'TEST_IDENTIFIER_USER{0}'.format(index))
            else:
                rs = cls_factory(subject_identifier='TEST_IDENTIFIER_USER{0}'.format(index))
            print('test {0} raises error if duplicate subject_identifier'.format(cls._meta.object_name))
            rs = cls.objects.get(subject_identifier='TEST_IDENTIFIER_USER{0}'.format(index))
            self.assertRaises(IdentifierError, cls_factory, subject_identifier='TEST_IDENTIFIER_USER{0}'.format(index))
            print('test {0} assigns uuid or study identifier if blank subject_identifier'.format(cls._meta.object_name))
            rs = cls_factory(subject_identifier=None)
            self.assertIsNotNone(rs.subject_identifier)
            if issubclass(cls, RegisteredSubject):
                self.assertTrue(re_pk.match(rs.subject_identifier))
            if issubclass(cls, TestConsent):
                self.assertTrue(rs.subject_identifier.startswith(settings.PROJECT_IDENTIFIER_PREFIX))
            print('test {0} unicode is masked if subject identifier is a uuid'.format(cls._meta.object_name))
            cls.objects.all().delete()
            rs = cls_factory()
            if re_pk.match(rs.subject_identifier):
                self.assertTrue('identifier not set' in str(rs))
            else:
                self.assertFalse('identifier not set' in str(rs))
