from . import BaseIdentifier


class SubjectIdentifier(BaseIdentifier):

    def __init__(self, identifier_format=None, **kwargs):
        super(SubjectIdentifier, self).__init__(
            identifier_format='{identifier_prefix}-{site_code}{device_id}{sequence}', **kwargs)
