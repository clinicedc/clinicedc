class SubjectScheduleError(Exception):
    pass


class NotOnScheduleError(Exception):
    pass


class OnScheduleError(Exception):
    pass


class OffScheduleError(Exception):
    pass


class NotOffScheduleError(Exception):
    pass


class NotOnScheduleForDateError(Exception):
    pass


class OnScheduleForDateError(Exception):
    pass


class OnScheduleFirstAppointmentDateError(Exception):
    pass


class UnknownSubjectError(Exception):
    pass


class InvalidOffscheduleDate(Exception):
    pass


class ScheduleError(Exception):
    pass


class ScheduledVisitWindowError(Exception):
    pass


class UnScheduledVisitWindowError(Exception):
    pass


class SiteVisitScheduleError(Exception):
    pass


class RegistryNotLoaded(Exception):
    pass


class AlreadyRegisteredVisitSchedule(Exception):
    pass


class VisitScheduleBaselineError(Exception):
    pass


class VisitScheduleNonCrfModelFormMixinError(Exception):
    pass
