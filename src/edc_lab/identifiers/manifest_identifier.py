from edc_identifier.simple_identifier import SimpleUniqueIdentifier


class ManifestIdentifier(SimpleUniqueIdentifier):

    random_string_length = 9
    identifier_type = 'manifest_identifier'
    template = 'M{device_id}{random_string}'
