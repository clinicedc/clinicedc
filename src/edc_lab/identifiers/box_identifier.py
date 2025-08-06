from edc_identifier.simple_identifier import SimpleUniqueIdentifier


class BoxIdentifier(SimpleUniqueIdentifier):
    random_string_length: int = 9
    identifier_type: str = "box_identifier"
    template: str = "B{device_id}{random_string}"
