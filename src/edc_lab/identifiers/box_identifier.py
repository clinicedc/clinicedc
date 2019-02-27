from edc_identifier.simple_identifier import SimpleUniqueIdentifier


class BoxIdentifier(SimpleUniqueIdentifier):

    random_string_length = 9
    identifier_type = "box_identifier"
    template = "B{device_id}{random_string}"
