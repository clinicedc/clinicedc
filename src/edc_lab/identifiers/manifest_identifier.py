from .base_identifier import Identifier


class ManifestIdentifier(Identifier):

    random_string_length = 9
    identifier_attr = 'manifest_identifier'
    template = 'M{device_id}{random_string}'
