from edc_auth.site_auths import site_auths
from edc_export.auth_objects import EXPORT

site_auths.update_group(
    "edc_visit_schedule.export_subjectschedulehistory",
    "edc_visit_schedule.export_visitschedule",
    name=EXPORT,
)
