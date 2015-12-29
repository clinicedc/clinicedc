import factory

from edc_consent.models import StudySite


class StudySiteFactory(factory.DjangoModelFactory):

    class Meta:
        model = StudySite

    site_code = factory.Sequence(lambda n: '1{0}'.format(n))
    site_name = factory.LazyAttribute(lambda o: 'Site_{0}'.format(o))
