from edc_auth.constants import EVERYONE
from edc_auth.site_auths import site_auths


def update_site_auths() -> None:
    site_auths.update_group("edc_visit_schedule.view_subjectschedulehistory", name=EVERYONE)


update_site_auths()
