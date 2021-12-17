from edc_auth.auth_objects import EVERYONE
from edc_auth.site_auths import site_auths
from edc_export.auth_objects import EXPORT

site_auths.update_group(
    "edc_visit_schedule.export_subjectschedulehistory",
    "edc_visit_schedule.export_visitschedule",
    name=EXPORT,
)

site_auths.update_group("edc_visit_schedule.view_subjectschedulehistory", name=EVERYONE)
