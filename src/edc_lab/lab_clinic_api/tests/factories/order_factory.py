import factory

from django.utils import timezone

from ...models import Order

from .aliquot_factory import AliquotFactory
from .panel_factory import PanelFactory


class OrderFactory(factory.DjangoModelFactory):

    class Meta:
        model = Order

    order_identifier = factory.Sequence(lambda n: n.rjust(8, '0'))
    order_datetime = timezone.now()
    aliquot = factory.SubFactory(AliquotFactory)
    panel = factory.SubFactory(PanelFactory)
