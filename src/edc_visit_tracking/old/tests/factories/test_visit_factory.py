import factory

from ..test_models import TestVisitModel


class TestVisitFactory(factory.DjangoModelFactory):
    class Meta:
        model = TestVisitModel
