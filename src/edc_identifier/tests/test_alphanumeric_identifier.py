from django.test import TestCase, tag

from ..alphanumeric_identifier import AlphanumericIdentifier


@tag('alpha')
class TestIdentifier(TestCase):

    
    def test_checkdigit(self):
        identifier = 'AAA00007'
        alpha_identifier = AlphanumericIdentifier(identifier)
        identifier_with_checkdigit = alpha_identifier.identifier
        identifier = alpha_identifier.remove_checkdigit(
            identifier_with_checkdigit)
        checkdigit = identifier_with_checkdigit.replace(identifier, '')
        self.assertEqual(checkdigit, '5')
        self.assertEqual(identifier_with_checkdigit, 'AAA00015')
        alpha_identifier.next()
        self.assertEqual(alpha_identifier.identifier, 'AAA00023')
        alpha_identifier.next()
        self.assertEqual(alpha_identifier.identifier, 'AAA00031')

    
    def test_alphanumeric(self):
        AlphanumericIdentifier.alpha_pattern = r'^[A-Z]{3}$'
        AlphanumericIdentifier.numeric_pattern = r'^[0-9]{4}$'
        AlphanumericIdentifier.seed = ['AAA', '0000']
        alpha_id = AlphanumericIdentifier(None)
        self.assertEqual(alpha_id.identifier, 'AAA00015')
        self.assertEqual(next(alpha_id), 'AAA00023')
        self.assertEqual(next(alpha_id), 'AAA00031')
        self.assertEqual(next(alpha_id), 'AAA00049')
        self.assertEqual(next(alpha_id), 'AAA00057')
        self.assertEqual(next(alpha_id), 'AAA00065')

    
    def test_alphanumeric_last(self):
        AlphanumericIdentifier.alpha_pattern = r'^[A-Z]{3}$'
        AlphanumericIdentifier.numeric_pattern = r'^[0-9]{4}$'
        AlphanumericIdentifier.seed = ['AAA', '0000']
        alpha_id = AlphanumericIdentifier('AAA99991')
        self.assertEqual(next(alpha_id), 'AAB00021')
        self.assertEqual(next(alpha_id), 'AAB00039')
        self.assertEqual(next(alpha_id), 'AAB00047')
        self.assertEqual(next(alpha_id), 'AAB00055')

#     
#     def test_increment_for_alphanumeric(self):
#         AlphanumericIdentifier.alpha_pattern = r'^[A-Z]{3}$'
#         AlphanumericIdentifier.numeric_pattern = r'^[0-9]{4}$'
#         AlphanumericIdentifier.seed = ['AAA', '0000']
#         instance = AlphanumericIdentifier(None)
#         self.assertEquals(instance.identifier, 'AAA00015')
#         for n in range(10000):
#             identifier = next(instance)
#             if n >= 9998:
#                 self.assertEqual('AAB', identifier[0:3])
#             else:
#                 self.assertEqual('AAA', identifier[0:3],
#                                  'Expected AAA for {}nth iteration. Got {}'.format(n, identifier))

    def test_alphanumeric_with_prefix(self):
        AlphanumericIdentifier.alpha_pattern = r'^[A-Z]{3}$'
        AlphanumericIdentifier.numeric_pattern = r'^[0-9]{4}$'
        AlphanumericIdentifier.seed = ['AAA', '0000']
        instance = AlphanumericIdentifier(prefix='ERIK')
        self.assertTrue(instance.identifier.startswith('ERIK'))
