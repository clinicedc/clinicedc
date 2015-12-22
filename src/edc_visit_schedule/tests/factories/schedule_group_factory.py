import factory
from edc.base.model.tests.factories import BaseUuidModelFactory
from ...models import ScheduleGroup

starting_seq_num = 1000


class ScheduleGroupFactory(BaseUuidModelFactory):
    FACTORY_FOR = ScheduleGroup

    group_name = factory.Sequence(lambda n: 'group_{0}'.format(n))
    membership_form = '0'
