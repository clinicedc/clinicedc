import factory

from edc_content_type_map.tests.factories import ContentTypeMapFactory
from edc_visit_schedule.tests.factories import VisitDefinitionFactory

from edc_meta_data.models import CrfEntry


class CrfEntryFactory(factory.DjangoModelFactory):
    class Meta:
        model = CrfEntry

    visit_definition = factory.SubFactory(VisitDefinitionFactory)
    content_type_map = factory.SubFactory(ContentTypeMapFactory)
    entry_order = factory.Sequence(lambda n: int(n) + 100)
