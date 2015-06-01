import factory

from django.conf import settings

from ...models import RegisteredSubject

from .base_subject_factory import BaseSubjectFactory


class RegisteredSubjectFactory(BaseSubjectFactory):

    identity = factory.Sequence(lambda n: '11111111{0}'.format(n))
    identity_type = 'OMANG'
    may_store_samples = 'Yes'

    class Meta:
        abstract = False
        model = RegisteredSubject
