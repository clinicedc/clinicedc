import re
import uuid

from django.apps import apps as django_apps
from django.core.exceptions import ImproperlyConfigured

from ...exceptions import IndentifierFormatError

from .check_digit import CheckDigit

app_config = django_apps.get_app_config('edc_identifier')
app_config_device = django_apps.get_app_config('edc_device')


class BaseSubjectIdentifier(object):

    def __init__(self, template=None, site_code=None, padding=None,
                 modulus=None, is_derived=None, add_check_digit=None,
                 using=None, identifier_prefix=None):

        self.add_check_digit = True if add_check_digit is None else add_check_digit
        self.template = template or "{identifier_prefix}-{site_code}{device_id}{sequence}"
        self.is_derived = False if is_derived is None else is_derived
        self.padding = padding or 4
        if not site_code:
            raise ImproperlyConfigured(
                'Attribute site_code cannot be None for a subject identifier. '
                'Specify the site_code when instantiating the identifier class.')
        self.site_code = site_code
        self.using = using or 'default'
        self.identifier_prefix = identifier_prefix or app_config.identifier_prefix
        self.modulus = modulus or app_config.identifier_modulus

    def get_identifier(self, add_check_digit=None, **kwargs):
        """ Returns a formatted identifier based on the identifier format and the dictionary
        of options.

        Arguments:
          add_check_digit: if true adds a check digit calculated using the numbers in the
            identifier. Letters are stripped out if they exist. (default: True)
          """
        from ...models import SubjectIdentifier
        self.subject_identifier = SubjectIdentifier.objects.using(self.using).create(
            identifier=str(uuid.uuid4()),
            padding=self.padding,
            is_derived=self.is_derived,
            device_id=app_config_device.device_id)
        try:
            new_identifier = self.template.format(**self.format_options())
        except KeyError:
            raise IndentifierFormatError(
                'Missing key/pair for identifier format. '
                'Got format {0} with dictionary {1}. Either correct the identifier '
                'format or provide a value for each place holder in the identifier '
                'format.'.format(self.template, self.format_options()))
        if self.add_check_digit:
            new_identifier = '{}-{}'.format(new_identifier, self.check_digit(new_identifier))
        self.subject_identifier.identifier = new_identifier
        self.subject_identifier.save(using=self.using)
        return new_identifier

    def format_options(self, **kwargs):
        format_options = {
            'identifier_prefix': self.identifier_prefix,
            'site_code': self.site_code}
        format_options.update(device_id=app_config_device.device_id)
        format_options.update(sequence=self.subject_identifier.formatted_sequence)
        if self.is_derived:
            format_options.update(sequence='')
        return format_options

    def check_digit(self, new_identifier):
        """Adds a check digit base on the integers in the identifier."""
        return CheckDigit().calculate(
            int(re.search('\d+', new_identifier.replace('-', '')).group(0)),
            self.modulus)
