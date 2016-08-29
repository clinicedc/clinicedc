import factory

from edc_lab.lab_clinic_api.tests.factories import PanelFactory
from edc_visit_schedule.tests.factories import VisitDefinitionFactory

from ...models import LabEntry


class LabEntryFactory(factory.DjangoModelFactory):
    class Meta:
        model = LabEntry

    visit_definition = factory.SubFactory(VisitDefinitionFactory)

    entry_order = factory.Sequence(lambda n: int(n) + 100)

    panel = factory.SubFactory(PanelFactory)
