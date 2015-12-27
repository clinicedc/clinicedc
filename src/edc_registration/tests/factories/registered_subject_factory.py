import factory

from edc_registration.models import RegisteredSubject


class RegisteredSubjectFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = RegisteredSubject

    identity = factory.Sequence(lambda n: '11111111{0}'.format(n))
    identity_type = 'OMANG'
    may_store_samples = 'Yes'
    subject_type = 'test_subject_type'
