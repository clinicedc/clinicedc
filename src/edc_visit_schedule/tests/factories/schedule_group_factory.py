import factory

from edc_visit_schedule.models import Schedule

starting_seq_num = 1000


class ScheduleFactory(factory.DjangoModelFactory):
    class Meta:
        model = Schedule

    group_name = factory.Sequence(lambda n: 'group_{0}'.format(n))
    membership_form = '0'
