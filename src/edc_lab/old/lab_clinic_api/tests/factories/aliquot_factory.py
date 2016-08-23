import factory


from ...models import Aliquot, AliquotCondition, AliquotType

from .receive_factory import ReceiveFactory


class AliquotConditionFactory(factory.DjangoModelFactory):
    class Meta:
        model = AliquotCondition


class AliquotTypeFactory(factory.DjangoModelFactory):
    class Meta:
        model = AliquotType


class AliquotFactory(factory.DjangoModelFactory):
    class Meta:
        model = Aliquot

    receive = factory.SubFactory(ReceiveFactory)
