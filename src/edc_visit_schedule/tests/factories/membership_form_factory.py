from edc.base.model.tests.factories import BaseUuidModelFactory
from ...models import MembershipForm

starting_seq_num = 1000


class MembershipFormFactory(BaseUuidModelFactory):
    FACTORY_FOR = MembershipForm

    content_type_map = '1'
    category = 'subject'
