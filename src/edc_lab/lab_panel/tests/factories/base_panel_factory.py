import factory


class BasePanelFactory(factory.django.DjangoModelFactory):

    class Meta:
        abstract = True

    name = factory.Sequence(lambda n: 'panel{0}'.format(n))
