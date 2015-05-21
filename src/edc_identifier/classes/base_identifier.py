import re
import uuid

from django.apps import apps
from django.conf import settings

from edc_device.device import Device

from ..exceptions import IdentifierError, IndentifierFormatError

from .check_digit import CheckDigit


class BaseIdentifier(object):
    """ Base class for all identifiers."""

    def __init__(
        self, identifier_format=None, app_name=None,
        model_name=None, site_code=None, padding=None,
        modulus=None, identifier_prefix=None, is_derived=False, add_check_digit=None, using=None,
        sequence_app_label=None, sequence_model_name=None
    ):
        self._sequence_app_label = None
        self._sequence_model_name = None
        self.padding = None
        self.modulus = None
        self.identifier_prefix = None
        self.site_code = None
        if add_check_digit is None:
            self.add_check_digit = True
        else:
            self.add_check_digit = add_check_digit
        self.using = using or 'default'
        self.is_derived = is_derived
        self.identifier_format = identifier_format or "{prefix}-{site_code}{device_id}{sequence}"
        self._sequence_app_label = sequence_app_label or 'edc_identifier'
        self._sequence_model_name = sequence_model_name or 'sequence'
        self.padding = padding or 4
        try:
            self.identifier_prefix = identifier_prefix or settings.IDENTIFIER_PREFIX
        except AttributeError:
            self.identifier_prefix = 'TEST01'
        try:
            self.modulus = modulus or settings.IDENTIFIER_MODULUS
        except AttributeError:
            modulus = modulus or 7
        self.identifier_history_model = apps.get_model(app_name, model_name)
        self.site_code = site_code or ''

    def _set_sequence_app_label(self, value):
        self._sequence_app_label = value

    def _set_sequence_model_name(self, value):
        self._sequence_model_name = value

    def _get_sequence_app_label(self):
        if not self._sequence_app_label:
            self._sequence_app_label()
        return self._sequence_app_label

    def _get_sequence_model_name(self):
        if not self._sequence_model_name:
            self._sequence_model_name()
        return self._sequence_model_name

    def get_identifier_prep(self, **kwargs):
        """ Users may override to pass non-default keyword arguments to get_identifier
        before the edc_identifier is created."""
        return {}

    def get_identifier_post(self, identifier, **kwargs):
        """ Users may override to run something after the edc_identifier is created.

        Must return the edc_identifier."""
        return identifier

    def _get_identifier_prep(self, **kwargs):
        """Calls user method self.get_identifier_prep() and adds/updates custom options to the defaults."""
        device = Device()
        options = {'identifier_prefix': self.identifier_prefix,
                   'site_code': self.site_code,
                   }
        options.update(device_id=device.device_id)
        custom_options = self.get_identifier_prep(**kwargs)
        if not isinstance(custom_options, dict):
            raise IdentifierError('Expected a dictionary from method get_identifier_prep().')
        if not self.identifier_format:
            raise AttributeError('Attribute identifier_format may not be None.')
        for k, v in custom_options.items():
            if k not in self.identifier_format:
                raise IndentifierFormatError(
                    'Unexpected keyword {0} for edc_identifier format {1}'.format(k, self.identifier_format))
            options.update({k: v})
        return options

    def _get_identifier_post(self, identifier, **kwargs):
        """Must return the edc_identifier."""
        identifier = self.get_identifier_post(identifier, **kwargs)
        return identifier

    def get_check_digit(self, base_new_identifier):
        """Adds a check digit base on the integers in the edc_identifier."""
        if not self.add_check_digit:
            return base_new_identifier
        else:
            check_digit = CheckDigit()
            return "{base}-{check_digit}".format(
                base=base_new_identifier,
                check_digit=check_digit.calculate(
                    int(re.search('\d+', base_new_identifier.replace('-', '')).group(0)), self.modulus))

    def _get_identifier_history_model_options(self):
        """Returns the options to create a new history model instance."""
        options = {
            'identifier': str(uuid.uuid4()),
            'padding': self.padding,
            "is_derived": self.is_derived,
            "sequence_app_label": self._get_sequence_app_label(),
            "sequence_model_name": self._get_sequence_model_name()}
        options.update(self.get_identifier_history_model_options())
        return options

    def get_identifier_history_model_options(self):
        """Users may override to add additional options."""
        return {}

    def get_identifier(self, add_check_digit=None, **kwargs):
        """ Returns a formatted edc_identifier based on the edc_identifier format and the dictionary
        of options.

        Arguments:
          add_check_digit: if true adds a check digit calculated using the numbers in the
            edc_identifier. Letters are stripped out if they exist. (default: True)
          """
        if self.add_check_digit is None:
            raise AttributeError('Instance attribute add_check_digit has not been set. Options are True/False')
        if add_check_digit:
            self.add_check_digit = add_check_digit
        # update the format options dictionary
        format_options = self._get_identifier_prep(**kwargs)
        if self.is_derived is None:
            raise AttributeError('Instance attribute is_derived has not been set. Options are True/False')
        self.identifier_model = self.identifier_history_model.objects.using(
            self.using).create(**self._get_identifier_history_model_options())
        format_options.update(sequence=self.identifier_model.formatted_sequence)
        if self.is_derived:
            # if derived, does not use a sequence number -- that is the sequence is in the base edc_identifier,
            # for example a maternal edc_identifier used as a base for an infant edc_identifier
            format_options.update(sequence='')
        # apply options to format to create a formatted edc_identifier
        try:
            new_identifier = self.identifier_format.format(**format_options)
        except KeyError:
            raise IndentifierFormatError(
                'Missing key/pair for edc_identifier format. '
                'Got format {0} with dictionary {1}. Either correct the edc_identifier '
                'format or provide a value for each place holder in the edc_identifier '
                'format.'.format(self.identifier_format, format_options))
        # check if adding a check digit
        if self.add_check_digit:
            new_identifier = self.get_check_digit(new_identifier)
        # call custom post method
        new_identifier = self._get_identifier_post(new_identifier, **kwargs)
        if not new_identifier:
            raise IdentifierError('Identifier cannot be None. Confirm overridden methods return the '
                                  'correct value. See BaseSubjectIdentifier')
        # update the edc_identifier model
        if self.identifier_model:
            self.identifier_model.identifier = new_identifier
            self.identifier_model.save(using=self.using)
        return new_identifier
