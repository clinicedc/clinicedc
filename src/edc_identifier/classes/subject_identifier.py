from . import BaseSubjectIdentifier


class SubjectIdentifier(BaseSubjectIdentifier):

    def __init__(self, identifier_format=None, app_name=None, model_name=None,
                 site_code=None, padding=None, modulus=None, identifier_prefix=None, using=None):
        identifier_format = '{identifier_prefix}-{site_code}{device_id}{sequence}'
        app_name = 'edc_identifier'
        model_name = 'subjectidentifier'
        is_derived = False
        super(SubjectIdentifier, self).__init__(
            identifier_format=identifier_format,
            app_name=app_name,
            model_name=model_name,
            site_code=site_code,
            padding=padding,
            modulus=modulus,
            identifier_prefix=identifier_prefix,
            is_derived=is_derived,
            using=using)
