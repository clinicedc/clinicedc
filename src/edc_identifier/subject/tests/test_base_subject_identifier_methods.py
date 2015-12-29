from django.test import TestCase
from django.conf import settings

from ..classes import BaseSubjectIdentifier
from ..exceptions import IndentifierFormatError
from ..models import Sequence


class TestBaseSubjectIdentifierMethods(TestCase):

    def test_p1(self):
        """Subject Identifier Tests."""
        print 'create 50 subject identifiers'
        site_code = '20'
        x = 0
        while x < 50:
            subject_identifier = BaseSubjectIdentifier(site_code=site_code)
            identifier = subject_identifier.get_identifier()
            print identifier
            self.assertTrue(identifier.startswith(settings.PROJECT_IDENTIFIER_PREFIX))
            self.assertTrue(identifier.startswith('{0}-{1}{2}'.format(settings.PROJECT_IDENTIFIER_PREFIX, site_code, settings.DEVICE_ID)))
            y = Sequence.objects.all().count()
            x += 1

        print ' ...this is the sequence table (sequence_number, source first identifier, device_id'
        for obj in Sequence.objects.all():
            print obj.id, obj.device_id

        print 'assert raises error if format has fewer keys that the values dictionary'
        subject_identifier = BaseSubjectIdentifier(identifier_format='{prefix}')
        self.assertRaises(IndentifierFormatError, subject_identifier.get_identifier)
        print 'assert raises error if format has more keys that the values dictionary'
        subject_identifier = BaseSubjectIdentifier(identifier_format='{identifier_prefix}-{site_code}{device_id}{sequence}{prefix}', site_code=site_code)
        self.assertRaises(IndentifierFormatError, subject_identifier.get_identifier)
        print 'assert raises error if get_identifier gets a value not in the format'
        subject_identifier = BaseSubjectIdentifier(identifier_format='{identifier_prefix}-{site_code}{device_id}{sequence}{prefix}', site_code=site_code)
        self.assertRaises(IndentifierFormatError, subject_identifier.get_identifier, erik=32)
