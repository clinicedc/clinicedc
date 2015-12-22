import factory

from edc_visit_schedule.models import ScheduleGroup

starting_seq_num = 1000


class ScheduleGroupFactory(factory.DjangoModelFactory):
    class Meta:
        model = ScheduleGroup

    group_name = factory.Sequence(lambda n: 'group_{0}'.format(n))
    membership_form = '0'
