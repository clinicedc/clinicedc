import factory
from datetime import datetime
from edc.base.model.tests.factories import BaseUuidModelFactory
from edc.core.bhp_content_type_map.tests.factories import ContentTypeMapFactory
from edc_consent import ConsentCatalogue


class ConsentCatalogueFactory(BaseUuidModelFactory):
    FACTORY_FOR = ConsentCatalogue

    name = 'edc_consent'
    content_type_map = factory.SubFactory(ContentTypeMapFactory)
    consent_type = 'study'
    version = '1'
    start_datetime = datetime(datetime.today().year - 1, 1, 1)
    end_datetime = datetime(datetime.today().year + 5, 1, 1)
    add_for_app = None
