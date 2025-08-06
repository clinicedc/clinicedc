from edc_identifier.simple_identifier import SimpleUniqueIdentifier


class RequisitionIdentifier(SimpleUniqueIdentifier):
    random_string_length: int = 5
    identifier_type: str = "requisition_identifier"
