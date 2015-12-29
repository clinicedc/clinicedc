from django.test import TestCase

from ..classes import Identifier
from ..exceptions import CheckDigitError, IdentifierEncodingError, IdentifierDecodingError
from ..models import IdentifierTracker


class TestIdentifierMethods(TestCase):

    def setUp(self):

        self.id = None
        if IdentifierTracker.objects.filter(identifier_string='123123123'):
            IdentifierTracker.objects.get(identifier_string='123123123').delete()

    def test_encoding(self):
        print 'TEST ENCODING'
        site_code = '10'
        mm = '02'
        yy = '13'
        IdentifierTracker.objects.all().delete()
        print 'instantiate identifier'
        identifier = Identifier(identifier_type='subject', site_code=site_code, mm=mm, yy=yy)
        print 'note: not calling create()'
        # check encode
        print 'assert 123123123 encodes to 21AYER'
        self.assertEqual(identifier.encode(123123123, 'base36'), '21AYER')
        print 'assert 21AYER decodes to 123123123'
        self.assertEqual(identifier.decode('21AYER', 'base36', has_check_digit=False), 123123123)
        print 'assert 123123125 encodes to 21AYET'
        self.assertEqual(identifier.encode(123123125, 'base36'), '21AYET')
        print 'assert 21AYET decodes to 123123125'
        self.assertEqual(identifier.decode('21AYET', 'base36', has_check_digit=False), 123123125)
        print 'encode 123123125 to 21AYET'
        self.assertEqual(identifier.encode(123123125, 'base36'), '21AYET')
        print 'decode 21AYET but specifiy has check digit (has_check_digit=True, modulus=7, check_digit_length=1)'
        self.assertEqual(identifier.decode('21AYET', 'base36', has_check_digit=True, modulus=7, check_digit_length=1), 123123125)
        print 'clear tracker table'
        IdentifierTracker.objects.all().delete()
        print 'instantiate identifier'
        identifier = Identifier(identifier_type='subject', site_code=site_code, counter_length=5, month=mm, year=yy)
        print 'assert encoding error; 123123123 does not encode to \'erik\''
        self.assertRaises(IdentifierEncodingError, identifier.encode, 123123123, 'erik')
        self.assertEqual(identifier.encode(123123125, 'base36'), '21AYET')
        print 'assert decoding error; 21AYET does not decode to \'erik\''
        self.assertRaises(IdentifierDecodingError, identifier.decode, '21AYET', 'erik', has_check_digit=False)
        print 'assert check digit error on decode; 21AYER does not have a valid check digit postfix (modulus=7, check_digit_length=1)'
        self.assertRaises(CheckDigitError, identifier.decode, '21AYER', 'base36', has_check_digit=True, modulus=7, check_digit_length=1)
        print 'ok'

    def test_create(self):
        print 'TEST CREATE'
        site_code = '10'
        protocol_code = '041'
        mm = '02'
        yy = '13'
        print 'clear tracker model'
        IdentifierTracker.objects.all().delete()
        print 'instantiate identifier'
        identifier = Identifier(identifier_type='subject', site_code=site_code, mm=mm, yy=yy)
        print 'assert that first identifier is 5YSHU'
        self.assertEqual(identifier.create(), '5YSHU')
        print ' assert 5YSHU is tracked'
        self.assertEqual(IdentifierTracker.objects.all()[0].identifier, '5YSHU')
        print 'assert it decodes to 10021314 (include check digit on decode)'
        self.assertEqual(identifier.decode('5YSHU', 'base36'), 10021314)
        print 'assert it decodes to 1002131 (do not include check digit on decode)'
        self.assertEqual(identifier.decode('5YSHU', 'base36', decoded_value_keeps_check_digit=False), 1002131)
        print 'create another identifier, should be 5YSI5'
        self.assertEqual(identifier.create(), '5YSI5')
        print 'assert it decodes to 1002132 which shows counter=2 (do not include check digit on decode)'
        self.assertEqual(identifier.decode('5YSI5', 'base36', decoded_value_keeps_check_digit=False), 1002132)
        print 'assert identifier.identifier is set'
        self.assertEqual(IdentifierTracker.objects.get(identifier='5YSI5').identifier, '5YSI5')
        print 'instantiate another identifier where site code is 20 and include protocol 041'
        identifier = Identifier(identifier_type='subject', site_code='20', protocol_code=protocol_code, mm=mm, yy=yy)
        print 'counter is reset to 0'
        self.assertEqual(identifier.get_counter(), 0)
        print 'create ...'
        self.assertEqual(identifier.create(), '97FWN0H')
        print 'is tracked ...'
        self.assertEqual(IdentifierTracker.objects.get(identifier='97FWN0H').identifier, '97FWN0H')
        print 'counter is incremented to 1'
        self.assertEqual(identifier.get_counter(), 1)
        print 'decodes to 20041021313 which is site, protocol, mm, yy, counter=1, check-digit=3'
        self.assertEqual(identifier.decode('97FWN0H', 'base36'), 20041021313)
        self.assertEqual(identifier.decode('97FWN0H', 'base36', decoded_value_keeps_check_digit=False), 2004102131)
        print 'create another identifier'
        self.assertEqual(identifier.create(), '97FWN0S')
        self.assertEqual(IdentifierTracker.objects.get(identifier='97FWN0S').identifier, '97FWN0S')
        print 'counter is incremented to 2'
        self.assertEqual(identifier.get_counter(), 2)
        print 'decodes to 20041021324 which is site, protocol, mm, yy, counter=2, check-digit=4'
        self.assertEqual(identifier.decode('97FWN0S', 'base36'), 20041021324)
        print 'try providing the root segment ... '
        print "assert raises error if root segment has a checkdigit that is invalid"
        self.assertRaises(CheckDigitError, identifier.create, root_segment='20041021310', has_check_digit=True, check_digit_length=1, modulus=7)
        print "assert next identifier is 2K2F2E4R if root segment is provided (20041021313) and no check digit and do not add one."
        self.assertEqual(identifier.create(root_segment='20041021313', has_check_digit=False, add_check_digit_if_missing=False), '2K2F2E4R')
        print 'counter is reset to 1 because the root segment changed'
        self.assertEqual(identifier.get_counter(), 1)
        print 'which manually decodes to 200410213131, note it just added the counter=1'
        decoded = int('2K2F2E4R', 36)
        self.assertEqual(200410213131, decoded)
        print 'and identifier instance decodes it to the same value'
        self.assertEqual(identifier.decode('2K2F2E4R', 'base36', has_check_digit=False), decoded)
        print 'create another for this root segment but this time have the check digit added'
        self.assertEqual(identifier.create(root_segment='20041021313', add_check_digit_if_missing=True), 'PKO6NXBV')
        print 'counter is incremented to 2'
        self.assertEqual(identifier.get_counter(), 2)
        print 'which manually decodes to 2004102131323'
        decoded = int('PKO6NXBV', 36)
        self.assertEqual(2004102131323, decoded)
        print 'which identifier decodes to 2004102131323, note it added the counter=2, check digit=3'
        self.assertEqual(identifier.decode('PKO6NXBV', 'base36', has_check_digit=True), decoded)
        print 'ok'

    def test_identifier_string(self):
        print 'TEST IDENTIFIER STRING'
        site_code = '10'
        protocol_code = '041'
        mm = '02'
        yy = '13'
        IdentifierTracker.objects.all().delete()
        identifier = Identifier(identifier_type='subject', mm=mm, yy=yy)
        self.assertEqual(identifier._get_identifier_string(), '1{0}{1}0'.format(mm, yy))
        IdentifierTracker.objects.all().delete()
        identifier = Identifier(identifier_type='subject', site_code=site_code, mm=mm, yy=yy)
        self.assertEqual(identifier._get_identifier_string(), '{0}{1}{2}0'.format(site_code, mm, yy))
        identifier = Identifier(identifier_type='subject', site_code=site_code, protocol_code=protocol_code, mm=mm, yy=yy)
        self.assertEqual(identifier._get_identifier_string(), '{0}{1}{2}{3}0'.format(site_code, protocol_code, mm, yy))
        identifier = Identifier(identifier_type='subject', site_code=site_code, protocol_code=protocol_code, mm=mm, yy=yy)
        self.assertEqual(identifier.create(), '4M25XMQ')
        self.assertEqual(identifier._get_identifier_string(), '10041021314')
        identifier.create()
        self.assertEqual(identifier._get_identifier_string(), '10041021325')
        print 'ok'
