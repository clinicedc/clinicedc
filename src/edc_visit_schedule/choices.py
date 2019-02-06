from .constants import HOURS, DAYS, WEEKS, MONTHS, YEARS, ON_SCHEDULE, OFF_SCHEDULE


SCHEDULE_STATUS = ((ON_SCHEDULE, "On schedule"), (OFF_SCHEDULE, "Off schedule"))

VISIT_INTERVAL_UNITS = (
    (HOURS, "Hours"),
    (DAYS, "Days"),
    (WEEKS, "Weeks"),
    (MONTHS, "Months"),
    (YEARS, "Years"),
)
