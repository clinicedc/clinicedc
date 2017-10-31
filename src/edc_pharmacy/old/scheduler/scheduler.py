from ..dispense_plan import dispense_plans
from .creators import DispenseScheduleCreator, DispenseAppointmentCreator
from .period import Period
from .schedule import Schedule
from .schedule_collection import ScheduleCollection


class SchedulerException(Exception):
    pass


class InvalidScheduleConfig(Exception):
    pass


class Scheduler:

    """Given enrolled subject, calculates the dispense schedules and create
    records for the subject.
    """

    schedule_collection_cls = ScheduleCollection
    dispense_timepoint_cls = DispenseAppointmentCreator
    dispense_schedule_creator_cls = DispenseScheduleCreator

    def __init__(self, subject_identifier=None, dispense_plan=None, arm=None,
                 randomization_datetime=None):
        self.subject_identifier = subject_identifier
        self.randomization_datetime = randomization_datetime
        self.arm = arm
        self.dispense_plan = dispense_plan or dispense_plans.get(arm)
        self.dispense_appointments = []
        if not self.dispense_plan:
            raise SchedulerException(
                f'Failed to find dispense schedule plan, for {self.arm}.')
        self.create_schedules()

    @property
    def subject_schedules(self):
        """Returns schedules calculated against a given dispense plan.
        """
        schedules = self.schedule_collection_cls()
        for schedule_name in self.dispense_plan or {}:
            self.validate_dispense_plan(dispense_plan=self.dispense_plan)
            schedule_details = self.dispense_plan.get(schedule_name)
            start_datetime = schedules.next_timepoint or self.randomization_datetime
            schedule_period = Period(
                start_datetime=start_datetime,
                unit=schedule_details.get('unit'),
                duration=schedule_details.get('duration'))
            schedule = Schedule(
                schedule_period,
                name=schedule_name,
                number_of_visits=schedule_details.get('number_of_visits'),
                description=schedule_details.get('description'))
            schedules.add(schedule=schedule)
        return schedules

    def validate_dispense_plan(self, dispense_plan):
        for item in dispense_plan or {}:
            try:
                plan = dispense_plan.get(item)
                plan['unit']
                plan['duration']
                plan['number_of_visits']
                plan['dispense_profile']
            except KeyError as e:
                raise InvalidScheduleConfig(f'Missing expected key {e}')

    def create_schedules(self):
        for sequence, schedule_name in enumerate(self.subject_schedules):
            sequence = sequence + 1
            schedule = self.subject_schedules.get(schedule_name)
            schedule_obj = self.dispense_schedule_creator_cls(
                arm=self.arm,
                schedule=schedule,
                subject_identifier=self.subject_identifier,
                sequence=sequence).create()
###
            schedule_plan = self.dispense_plan.get(schedule_name)
            appointments = self.dispense_timepoint_cls(
                schedule_name=schedule_name, schedule_plan=schedule_plan,
                schedule=schedule_obj,
                timepoints=schedule.visits,
                subject_identifier=self.subject_identifier
            ).create()
            self.dispense_appointments.extend(appointments)
