from edc_identifier.simple_identifier import SimpleUniqueIdentifier


class ScreeningIdentifier(SimpleUniqueIdentifier):
    # TODO: is this connected to edc_protocol.screening_identifier_pattern ??
    random_string_length = 7
    identifier_type = "screening_identifier"
    template = "S{device_id}{random_string}"
