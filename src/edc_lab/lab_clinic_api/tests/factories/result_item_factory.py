import factory

from django.utils import timezone

from ...models import ResultItem

from .result_factory import ResultFactory
from .test_code_factory import TestCodeFactory


class ResultItemFactory(factory.DjangoModelFactory):
    class Meta:
        model = ResultItem

    result = factory.SubFactory(ResultFactory)
    test_code = factory.SubFactory(TestCodeFactory)
    result_item_value = factory.Sequence(lambda n: '{0}'.format(n))
    result_item_datetime = timezone.now()
    validation_status = 'F'
    receive_identifier = ''
