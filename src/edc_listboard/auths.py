from edc_auth.auth_objects import CLINIC
from edc_auth.site_auths import site_auths

from .auth_objects import listboard_tuples

site_auths.add_custom_permissions_tuples(
    model="edc_listboard.listboard", codename_tuples=listboard_tuples
)

site_auths.update_group(
    "edc_listboard.view_subject_listboard",
    "edc_listboard.view_subject_review_listboard",
    name=CLINIC,
)
