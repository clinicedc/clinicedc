import factory

from datetime import date

from edc_subject.models import BaseSubject


class BaseSubjectFactory(factory.DjangoModelFactory):

    # if you set subject_identifier here, filling in a consent, for example, will not generate
    # an identifier and not update registered subject -- so don't
    # subject_identifier = factory.Sequence(lambda n: '{0}-{1}{2}-0'.format(settings.PROJECT_IDENTIFIER_PREFIX, settings.DEVICE_ID, n.rjust(5, '0')))
    first_name = factory.Sequence(lambda n: 'ERIK{0}'.format(n))
    last_name = factory.Sequence(lambda n: 'VAN{0}'.format(n))
    initials = factory.Sequence(lambda n: 'E{0}V'.format(n))
    dob = date(date.today().year - 20, 1, 1)
    is_dob_estimated = '-'
    gender = 'M'
    subject_type = 'test_subject_type'

    class Meta:
        model = BaseSubject
        abstract = True
