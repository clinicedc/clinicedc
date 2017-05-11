from ..exceptions import RequisitionError

from edc_identifier.simple_identifier import SimpleIdentifier


class RequisitionIdentifier(SimpleIdentifier):

    random_string_length = 5
    identifier_attr = 'requisition_identifier'
    error_class = RequisitionError
