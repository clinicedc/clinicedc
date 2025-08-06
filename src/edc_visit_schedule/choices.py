from .constants import DAYS, HOURS, MONTHS, OFF_SCHEDULE, ON_SCHEDULE, WEEKS, YEARS

SCHEDULE_STATUS = ((ON_SCHEDULE, "On schedule"), (OFF_SCHEDULE, "Off schedule"))

VISIT_INTERVAL_UNITS = (
    (HOURS, "Hours"),
    (DAYS, "Days"),
    (WEEKS, "Weeks"),
    (MONTHS, "Months"),
    (YEARS, "Years"),
)
