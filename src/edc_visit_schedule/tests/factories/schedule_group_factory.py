import factory
from edc_base.model.tests.factories import BaseUuidModelFactory
from edc_visit_schedule.models import ScheduleGroup

starting_seq_num = 1000


class ScheduleGroupFactory(BaseUuidModelFactory):
    FACTORY_FOR = ScheduleGroup

    group_name = factory.Sequence(lambda n: 'group_{0}'.format(n))
    membership_form = '0'
