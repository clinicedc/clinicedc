from edc_identifier.simple_identifier import SimpleUniqueIdentifier


class ManifestIdentifier(SimpleUniqueIdentifier):
    random_string_length: int = 9
    identifier_type: str = "manifest_identifier"
    template: str = "M{device_id}{random_string}"
