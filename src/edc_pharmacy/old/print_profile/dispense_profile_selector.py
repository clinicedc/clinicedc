from ..models import DispenseAppointment


class DispenseProfileSelector:
    """Given enrolled subject, schedule_name and dispense_plan,
    this class determines dispense profile whether it is enrollment profile
    or followup profile.
    """

    def __init__(self, subject_identifier=None, schedule_name=None,
                 schedule_plan=None):
        self.subject_identifier = subject_identifier
        self.schedule_plan = schedule_plan
        self.schedule_name = schedule_name

    @property
    def profile(self):
        try:
            profile = self.schedule_plan.get(
                'dispense_profile').get('enrollment')
            DispenseAppointment.objects.get(
                schedule__subject_identifier=self.subject_identifier,
                profile_label=f'{profile.label}',
                schedule__name=self.schedule_name
            )
            profile = self.schedule_plan.get(
                'dispense_profile').get('followup')
        except DispenseAppointment.DoesNotExist:
            pass
        return profile
