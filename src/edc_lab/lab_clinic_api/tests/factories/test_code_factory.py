import factory

from ...models import TestCode, TestCodeGroup
from lis.choices import UNITS


class TestCodeFactory(factory.DjangoModelFactory):
    class Meta:
        model = TestCode

    code = factory.Sequence(lambda n: 'CODE{0}'.format(n))
    name = factory.Sequence(lambda n: 'NAME{0}'.format(n))
    units = factory.Iterator(UNITS, getter=lambda c: c[0])
    display_decimal_places = 2


class TestCodeGroupFactory(factory.DjangoModelFactory):

    class Meta:
        model = TestCodeGroup
