import factory

from datetime import date

from edc_registration.tests.factories import RegisteredSubjectFactory


class BaseOffStudyFactory(factory.DjangoModelFactory):
    ABSTRACT_FACTORY = True

    registered_subject = factory.SubFactory(RegisteredSubjectFactory)
    offstudy_date = date.today()
    reason = 'reason'
