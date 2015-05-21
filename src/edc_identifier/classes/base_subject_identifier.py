from django.core.exceptions import ImproperlyConfigured
from django.conf import settings

from . import BaseIdentifier


class BaseSubjectIdentifier(BaseIdentifier):
    """ Base class for all identifiers."""

    def __init__(self, identifier_format=None, app_name=None, model_name=None,
                 site_code=None, padding=None, modulus=None, identifier_prefix=None,
                 is_derived=False, add_check_digit=None, using=None):
        app_name = app_name or 'edc_identifier'
        model_name = model_name or 'subjectidentifier'
        identifier_format = identifier_format or "{identifier_prefix}-{site_code}{device_id}{sequence}"
        if 'site_code' in identifier_format:
            if not site_code:
                raise ImproperlyConfigured(
                    'Attribute site_code cannot be None for a subject edc_identifier. Specify the '
                    'site_code when instantiating the edc_identifier class.')
        super(BaseSubjectIdentifier, self).__init__(
            identifier_format=identifier_format,
            app_name=app_name,
            model_name=model_name,
            site_code=site_code,
            padding=padding,
            modulus=modulus,
            identifier_prefix=identifier_prefix,
            is_derived=is_derived,
            add_check_digit=add_check_digit,
            using=using)
