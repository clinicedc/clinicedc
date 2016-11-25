from faker import Faker
from faker.providers import BaseProvider

from .requisition_identifier import RequisitionIdentifier


class EdcProvider(BaseProvider):

    def requisition_identifier(self):
        return RequisitionIdentifier().identifier


edc_faker = Faker()
edc_faker.add_provider(EdcProvider)
