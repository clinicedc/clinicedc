from faker.providers import BaseProvider

from ..requisition_identifier import RequisitionIdentifier


class EdcLabProvider(BaseProvider):

    def requisition_identifier(self):
        return RequisitionIdentifier().identifier
