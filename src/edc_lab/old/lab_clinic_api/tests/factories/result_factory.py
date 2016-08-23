import factory

from django.utils import timezone

from ...models import Result

from .order_factory import OrderFactory


class ResultFactory(factory.DjangoModelFactory):
    class Meta:
        model = Result

    order = factory.SubFactory(OrderFactory)
    result_identifier = factory.Sequence(lambda n: n.rjust(8, '0'))
    result_datetime = timezone.now()
