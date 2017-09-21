from edc_identifier.simple_identifier import SimpleIdentifier

from ..exceptions import RequisitionError


class RequisitionIdentifier(SimpleIdentifier):

    random_string_length = 5
    identifier_type = 'requisition_identifier'
    error_class = RequisitionError
