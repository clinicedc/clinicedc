from ..exceptions import RequisitionError

from .base_identifier import Identifier


class RequisitionIdentifier(Identifier):

    random_string_length = 5
    identifier_attr = 'requisition_identifier'
    error_class = RequisitionError
