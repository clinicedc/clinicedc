from dateutil.relativedelta import relativedelta


class AppointmentDescriber:

    """Given dispense appointment,  this class returns human readiable 
    description about the dispense timepoint.

    For Example.
        Schedule(start_date=01-10-2017, end_date=03-10-2017): Day 1 - Day 3
        Schedule is divided into 2 dispense timepoint.
        1. DispenseTimepoint(timepoint=01-10-2017) returns Day 1
        2. DispenseTimepoint(timepoint=03-10-2017) returns Day 2 to Day 3
    """

    def __init__(self, dispense_appointment=None):
        self.dispense_appointment = dispense_appointment

    @property
    def start_day(self):
        if not self.dispense_appointment.previous():
            return 'Day 1'
        else:
            _, days = self.count_days(
                dispense_appointment=self.dispense_appointment.previous())
            next_day = days + 1
            return f'Day {next_day}'

    @property
    def end_day(self):
        if self.dispense_appointment.previous():
            _, days = self.count_days(
                dispense_appointment=self.dispense_appointment.previous())
            _, current_days = self.count_days(
                dispense_appointment=self.dispense_appointment)
            next_day = days + 1
            end_day = next_day + current_days
            return f'Day {end_day}'
        else:
            _, current_days = self.count_days(
                dispense_appointment=self.dispense_appointment)
            return f'Day {current_days}'

    @property
    def end_date(self):
        end_date, _ = self.count_days(
            dispense_appointment=self.dispense_appointment)
        return end_date

    def human_readiable(self):
        """Returns description of dispense timepoint example.
        (2017-08-24):day 1 to (2017-08-31): day 7.
        """
        description = (f'({self.dispense_appointment.appt_datetime}):'
                       f'{self.start_day} to ({self.end_date}):'
                       f'{self.end_day}')
        return description

    def is_next_pending_appointment(self):
        from edc_pharma.models import DispenseAppointment
        dispense_appointment = DispenseAppointment.objects.filter(
            schedule__subject_identifier=self.dispense_appointment.schedule.subject_identifier,
            is_dispensed=False
        ).order_by('appt_datetime').first()
        is_dispensed = True if dispense_appointment.id == self.dispense_appointment.id else False
        return is_dispensed

    @property
    def duration(self):
        return self.count_days(
            dispense_appointment=self.dispense_appointment)[1]

    def count_days(self, dispense_appointment=None):
        """Returns count of days between two dispense timepoints.
        """
        next_timepoint = None
        end_timepoint = dispense_appointment.schedule.end_datetime
        if dispense_appointment.next():
            dispense_appointment_obj = dispense_appointment.next()
            next_timepoint = dispense_appointment_obj.appt_datetime
            end_timepoint = next_timepoint - relativedelta(days=1)
        next_timepoint = (
            next_timepoint or dispense_appointment.schedule.end_datetime)
        current_timepoint = dispense_appointment.appt_datetime
        return (end_timepoint, (end_timepoint - current_timepoint).days)
