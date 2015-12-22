import factory

from edc_visit_schedule.models import MembershipForm

starting_seq_num = 1000


class MembershipFormFactory(factory.DjangoModelFactory):

    class Meta:
        model = MembershipForm

    content_type_map = '1'
    category = 'subject'
