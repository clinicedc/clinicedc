import factory

from edc.base.model.tests.factories import BaseUuidModelFactory
from edc.core.bhp_content_type_map.tests.factories import ContentTypeMapFactory

from edc.subject.visit_schedule.models import VisitDefinition

starting_seq_num = 1000


class VisitDefinitionFactory(BaseUuidModelFactory):

    class Meta:
        model = VisitDefinition

    code = factory.Sequence(lambda n: 'CODE{0}'.format(n))
    title = factory.Sequence(lambda n: 'TITLE{0}'.format(n))
    visit_tracking_content_type_map = factory.SubFactory(ContentTypeMapFactory)
