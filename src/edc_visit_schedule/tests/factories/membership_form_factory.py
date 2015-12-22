from edc_base.model.tests.factories import BaseUuidModelFactory
from edc_visit_schedule.models import MembershipForm

starting_seq_num = 1000


class MembershipFormFactory(BaseUuidModelFactory):
    FACTORY_FOR = MembershipForm

    content_type_map = '1'
    category = 'subject'
