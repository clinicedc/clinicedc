import factory

from ...models import Panel


class PanelFactory(factory.DjangoModelFactory):
    class Meta:
        model = Panel

    name = factory.Sequence(lambda n: 'panel{0}'.format(n))
    panel_type = factory.Sequence(lambda n: 'TEST{0}'.format(n))
