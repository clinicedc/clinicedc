import factory

from edc_visit_schedule.models import VisitDefinition

from edc.core.bhp_content_type_map.tests.factories import ContentTypeMapFactory

starting_seq_num = 1000


class VisitDefinitionFactory(factory.DjangoModelFactory):

    class Meta:
        model = VisitDefinition

    code = factory.Sequence(lambda n: 'CODE{0}'.format(n))
    title = factory.Sequence(lambda n: 'TITLE{0}'.format(n))
    visit_tracking_content_type_map = factory.SubFactory(ContentTypeMapFactory)
