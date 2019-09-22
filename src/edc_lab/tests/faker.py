from faker.providers import BaseProvider

from edc_lab.identifiers import RequisitionIdentifier


class EdcLabProvider(BaseProvider):
    def requisition_identifier(self):
        return RequisitionIdentifier().identifier
