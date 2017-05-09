from faker.providers import BaseProvider

from ..identifiers import RequisitionIdentifier


class EdcLabProvider(BaseProvider):

    def requisition_identifier(self):
        return RequisitionIdentifier().identifier
