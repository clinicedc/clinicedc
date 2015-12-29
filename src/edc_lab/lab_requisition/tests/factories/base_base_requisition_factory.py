import factory

from datetime import datetime


class BaseBaseRequisitionFactory(factory.DjangoModelFactory):
    class Meta:
        abstract = True

    requisition_identifier = factory.Sequence(lambda n: str(n).rjust(8, '0'))
    requisition_datetime = datetime.today()
    study_site = '40'
    drawn_datetime = datetime.today()
