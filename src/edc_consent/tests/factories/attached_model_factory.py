import factory
from edc.base.model.tests.factories import BaseUuidModelFactory
from ...models import AttachedModel
from .consent_catalogue_factory import ConsentCatalogueFactory


class AttachedModelFactory(BaseUuidModelFactory):
    FACTORY_FOR = AttachedModel

    consent_catalogue = factory.SubFactory(ConsentCatalogueFactory)
    content_type_map = ''
    is_active = True
