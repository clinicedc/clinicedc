import re

from datetime import datetime

from django.db import IntegrityError

from ..exceptions import (IdentifierError, CheckDigitError, IdentifierEncodingError,
                          IdentifierDecodingError, IndentifierFormatError)
from ..models import IdentifierTracker


class Identifier(object):

    """
    Create or increment edc_identifier base36 encoded based on a given site_code
    and the year.

    Parts of Encode(), Decode() from http://en.wikipedia.org/wiki/Base_36
    """

    def __init__(self, **kwargs):
        self._counter_segment = None
        self._counter_length = None
        self._root_length = None
        self._root_segment = None
        self._pad_char = None
        self._modulus = None
        self._counter = None
        self._encoding = None
        self._identifier_tracker = None
        self._identifier = None
        self._identifier_string = None
        self._locked = False
        self._add_check_digit_to_identifier = None
        self._check_digit_length = None
        self._mm = kwargs.get('mm', str(datetime.now().strftime('%m')))
        self._yy = kwargs.get('yy', str(datetime.now().strftime('%y')))
        self.set_site_code(kwargs.get('site_code', '1'))
        self.protocol_code = kwargs.get('protocol_code', '')
        self.set_encoding(kwargs.get('encoding', 'base36'))
        self.set_counter_length(kwargs.get('counter_length', 1))
        self.set_identifier_type(kwargs.get('identifier_type', 'unknown'))

    def __str__(self):
        return self.get_identifier()

    def create(self, root_segment=None, counter_length=None, has_check_digit=None,
               modulus=None, check_digit_length=None, add_check_digit_if_missing=None):
        """Create a new edc_identifier."""
        # either root_segment has a check digit or it will get one BEFORE encoding
        self._has_check_digit = has_check_digit
        if has_check_digit is True:
            self._add_check_digit_to_identifier = False
        else:
            if add_check_digit_if_missing is None:
                self._add_check_digit_to_identifier = True  # default value
            else:
                self._add_check_digit_to_identifier = add_check_digit_if_missing
        if has_check_digit:
            if not check_digit_length:
                raise TypeError(
                    'Argument \'check_digit_length\' cannot be None if the root_segment '
                    'provided \'has_check_digit\'. Specify the length of the check digit '
                    'for root_segment {0}'.format(root_segment))
            else:
                self.set_check_digit_length(check_digit_length)
            if not modulus:
                raise TypeError(
                    'Argument \'modulus\' cannot be None if the root_segment provided '
                    '\'has_check_digit\'. Specify the modulus to calculate check digit '
                    'for root_segment {0}'.format(root_segment))
            else:
                self.set_modulus(modulus)
        if has_check_digit and add_check_digit_if_missing:
            raise TypeError('Both has_check_digit and add_check_digit_if_missing cannot be True')
        if counter_length:
            self.set_counter_length(counter_length)
        self.set_root_segment(root_segment)
        self._set_identifier()
        return self.get_identifier()

    def create_with_root(self, root_segment, counter_length=None):

        """Create a new system-wide unique edc_identifier with a given root segment
        with or without a counter segment depending on the value of
        counter_length.
        """
        return self.create(root_segment, counter_length)

    def get_lock(self):
        return self._locked

    def lock(self):
        self._locked = True

    def unlock(self):
        self._locked = False

    def get_check_digit(self, number):
        """ Adds a check_digit to number. """
        try:
            number = int(number)
        except TypeError:
            raise CheckDigitError('Expected an integer to calculate the check digit. Got {}'.format(number))
        cd = number % self.get_modulus()
        self.set_check_digit_length(len(str(cd)))
        return cd

    def increment(self, identifier_tracker=None):
        """Increments last counter by 1 using last counter (or None) from IdentifierTracker model
           for given root_segment and create a new IdentifierTracker record.

         .. note:: counter is incremented for each root segment. so if the root segment changes
                   the counter is reset.
           """

        # search for last edc_identifier with this root segment
        last_identifier = IdentifierTracker.objects.filter(
            root_number=self.get_root_segment()).order_by('-counter')
        # increment
        if last_identifier:
            self.set_counter(last_identifier[0].counter + 1)
        else:
            # ... or start at 1 for new root segment
            self.set_counter(1)
        try:
            if isinstance(identifier_tracker, IdentifierTracker):
                identifier_tracker.counter = self.get_counter()
                self._identifier_tracker = identifier_tracker
            else:
                # create record, we'll update with the edc_identifier later
                self._identifier_tracker = IdentifierTracker(
                    root_number=self.get_root_segment(),
                    counter=self.get_counter(),
                    identifier_type=self.get_identifier_type(),
                )
            self._identifier_tracker.save()
        except IntegrityError as e:
            raise e
        except:
            raise IdentifierError(
                'Failed to save() to IdentifierTracker table, your edc_identifier was '
                'not created. Is it unique?')

    def update_tracker(self):
        """update our IdentifierTracker record with created edc_identifier"""
        self._identifier_tracker.identifier = self.get_identifier()
        self._identifier_tracker.identifier_string = self._get_identifier_string()
        self._identifier_tracker.save()

    def set_site_code(self, value):
        value = str(value)
        if not re.match('\d+', value):
            raise IndentifierFormatError('Site code must be a string of numbers. Got {0}.'.format(value))
        self._site_code = value

    def get_site_code(self):
        return self._site_code

    def set_root_length(self, value):
        self._root_length = value

    def get_root_length(self):
        if not self._root_length:
            self.set_root_length()
        return self._root_length

    def set_given_root_segment(self, value):
        self._given_root_segment = value

    def get_given_root_segment(self):
        if not self._given_root_segment:
            self.set_given_root_segment(None)
        return self._given_root_segment

    def set_root_segment(self, value=None):
        """Derives the root segment of the edc_identifier from either a given segment
        or site, protocol, date."""
        if value:
            if self._has_check_digit:
                # confirm the check digit is valid
                check_digit_length = self.get_check_digit_length()
                if not int(value[0:-check_digit_length]) % self.get_modulus() == int(value[-check_digit_length]):
                    raise CheckDigitError(
                        'Invalid unencoded_value. Has_check_digit=True so last digit should be %s '
                        'which is the modulus %s of %s, Got %s' % (
                            int(value[0:-check_digit_length]) % self.get_modulus(),
                            self.get_modulus(),
                            value[0:-check_digit_length],
                            value[-check_digit_length]))
            self._root_segment = str(value)
        else:
            """Set root_segment, un-encoded root_segment, as
            site_code + protocol_code + 2digitmonth + 2digityear"""
            self._root_segment = "%s%s%s%s" % (
                self.get_site_code(), self.protocol_code, self._mm, self._yy.rjust(2, '0'))
        self.set_root_length(len(self._root_segment))

    def get_root_segment(self):
        if not self._root_segment:
            self.set_root_segment()
        return self._root_segment

    def get_counter_segment(self):
        if self.get_counter_length() == 0:
            # in this case, edc_identifier string will have no counter segment
            return ''
        else:
            return str(self.get_counter()).rjust(self.get_counter_length(), self.get_pad_char())

    def set_counter_length(self, value):
        if not isinstance(value, int):
            raise TypeError('Counter length must be an integer.')
        if not value > 0:
            raise IdentifierError('Identifier counter length must be greater than 0. Got {0}.'.format(value))
        self._counter_length = value

    def get_counter_length(self):
        if self._counter_length is None:
            raise IdentifierError('Counter length cannot be None. Set in __init__.')
        return self._counter_length

    def set_counter(self, value=None):
        if not value:
            value = 0
        self._counter = value

    def get_counter(self):
        if not self._counter:
            self.set_counter()
        return self._counter

    def set_modulus(self, value=None):
        if not value:
            value = 7
        if not isinstance(value, int):
            raise IdentifierError('Modulus must be an integer. Got {0}'.format(value))
        self._modulus = value

    def get_modulus(self):
        if not self._modulus:
            self.set_modulus()
        return self._modulus

    def set_check_digit_length(self, value):
        """Sets the check digit length that is set when the check digit is calculated."""
        self._check_digit_length = value

    def get_check_digit_length(self):
        """Gets the check digit length that is set when the check digit is calculated."""
        if not self._check_digit_length:
            raise TypeError('Attribute self._check_digit_length cannot be None.')
        return self._check_digit_length

    def set_pad_char(self, value=None):
        if not value:
            value = '0'
        self._pad_char = value

    def get_pad_char(self):
        if not self._pad_char:
            self.set_pad_char()
        return self._pad_char

    def set_encoding(self, value):
        self._encoding = value

    def get_encoding(self):
        if not self._encoding:
            raise IdentifierError('Encoding cannot be None.')
        return self._encoding

    def _set_identifier(self):
        # before encoding, increment counter for this root_segment and create an IdentifierTracker record
        self.increment()
        # set the edc_identifier
        self._identifier = self.encode(int(self._get_identifier_string()), self.get_encoding())
        # check if edc_identifier is unique
        while self._identifier_tracker.__class__.objects.filter(identifier=self._identifier).exists():
            self.increment()
            self._identifier = self.encode(int(self._get_identifier_string()), self.get_encoding())
        # update the tracker
        self.update_tracker()

    def get_identifier(self):
        if not self._identifier:
            raise IdentifierError('Attribute self._identifier cannot be None. Call set_identifier() or create() first.')
        return self._identifier

    def _get_identifier_string(self):
        """Concat string of self._root_segment with padded string of counter, which must be able to convert to an INT.

        ..note: always adds a counter segment, optionally adds a check digit."""
        string = "{0}{1}".format(self.get_root_segment(), self.get_counter_segment())
        if string[0] == '0':
            raise IndentifierFormatError('Identifier string cannot start with \'0\'. Got {0}'.format(string))
        check_digit = ''
        if self._add_check_digit_to_identifier:
            check_digit = self.get_check_digit(int(string))
        return "{0}{1}{2}".format(self.get_root_segment(), self.get_counter_segment(), check_digit)

    def set_identifier_type(self, value):
        self._identifier_type = value

    def get_identifier_type(self):
        return self._identifier_type

    def encode(self, unencoded_value, encoding, alphabet=None):
        """Converts positive integer to a base36 string."""
        if not alphabet:
            alphabet = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        if not isinstance(unencoded_value, (int)):
            raise IdentifierEncodingError(
                'unencoded_value passed for encoding must be an integer. Got {0}'.format(unencoded_value))
        if encoding:
            if encoding == 'base36':
                # Special case for zero
                if unencoded_value == 0:
                    encoded_value = alphabet[0]
                base36 = ''
                sign = ''
                if unencoded_value < 0:
                    sign = '-'
                    unencoded_value = -unencoded_value
                while unencoded_value != 0:
                    unencoded_value, i = divmod(unencoded_value, len(alphabet))
                    base36 = alphabet[i] + base36
                encoded_value = sign + base36
            else:
                raise IdentifierEncodingError(
                    'Invalid or unhandled encoding parameter. Got {0}'.format(encoding))
        if not encoded_value:
            raise IdentifierEncodingError('Value was not encoded.')
        return encoded_value

    def decode(self, encoded_value, encoding, has_check_digit=None, check_digit_length=None,
               modulus=None, decoded_value_keeps_check_digit=None):
        """Decodes an encoded value and handles check digit if it has one.

        ..warning:: This only works of check digit is a single digit, so must be mod7"""
        if has_check_digit is None:
            has_check_digit = True  # default
        if has_check_digit and not check_digit_length:
            check_digit_length = self.get_check_digit_length()
        if decoded_value_keeps_check_digit is None:
            decoded_value_keeps_check_digit = True
        if not modulus:
            modulus = self.get_modulus()
        if encoding == 'base36':
            decoded_number = str(int(encoded_value, 36))
        else:
            raise IdentifierDecodingError(
                'Attribute encoding is invalid or unhandled. Got {0}'.format(encoding))
        if has_check_digit:
            # assume last digit is the check digit
            if not int(decoded_number[0:-check_digit_length]) % modulus == int(decoded_number[-check_digit_length]):
                check_digit = int(decoded_number[0:-1]) % modulus
                raise CheckDigitError(
                    'Invalid edc_identifier after decoding. Last digit should be {0} which '
                    'is the modulus {1} of {2}, Got {3}'.format(
                        check_digit, modulus, decoded_number[0:-1], decoded_number[-1]))
            else:
                if not decoded_value_keeps_check_digit:
                    decoded_number = decoded_number[0:-check_digit_length]
        return int(decoded_number)
