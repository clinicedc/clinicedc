import factory

from edc_registration.tests.factories import RegisteredSubjectFactory

from ...models import Receive


class ReceiveFactory(factory.DjangoModelFactory):
    class Meta:
        model = Receive

    registered_subject = factory.SubFactory(RegisteredSubjectFactory)
