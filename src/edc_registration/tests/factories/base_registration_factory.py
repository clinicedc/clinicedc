import factory
from datetime import datetime

from .registered_subject_factory import RegisteredSubjectFactory


class BaseRegistrationFactory(factory.DjangoModelFactory):
    ABSTRACT_FACTORY = True

    registered_subject = factory.SubFactory(RegisteredSubjectFactory)
    registration_datetime = datetime.today()
