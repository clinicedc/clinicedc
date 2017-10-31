

class ScheduleOverlapError(Exception):
    pass


class ScheduleValidator:

    def __init__(self, schedules=None):
        for key in schedules:
            schedule = schedules.get(key)
            for key in schedules:
                vschedule = schedules.get(key)
                if schedule.name == vschedule.name:
                    continue
                if (schedule.period.start_datetime <= vschedule.period.end_datetime
                        <= schedule.period.end_datetime):
                    raise ScheduleOverlapError(
                        f'Overlap between {schedule.name} '
                        f'and {vschedule.name}. Check schedule period dates.')
                if (schedule.period.start_datetime <= vschedule.period.start_datetime
                        <= schedule.period.end_datetime):
                    raise ScheduleOverlapError(
                        f'Overlap between {schedule.name} and {vschedule.name}.'
                        f' {vschedule.name} startdate should not fall in range '
                        f'{schedule.period.start_datetime.date()} to '
                        f'{schedule.period.end_datetime.date()} )')
