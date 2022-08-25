from edc_auth.auth_objects import EVERYONE
from edc_auth.site_auths import site_auths

site_auths.update_group("edc_visit_schedule.view_subjectschedulehistory", name=EVERYONE)
