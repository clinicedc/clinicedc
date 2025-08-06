from edc_auth.constants import AUDITOR_ROLE, CLINICIAN_ROLE, NURSE_ROLE
from edc_auth.site_auths import site_auths

REPORTABLE_SUPER = "REPORTABLE"
REPORTABLE_VIEW = "REPORTABLE_VIEW"


reportable_codenames = [
    "edc_reportable.add_normaldata",
    "edc_reportable.change_normaldata",
    "edc_reportable.view_normaldata",
    "edc_reportable.delete_normaldata",
    "edc_reportable.add_gradingdata",
    "edc_reportable.change_gradingdata",
    "edc_reportable.view_gradingdata",
    "edc_reportable.delete_gradingdata",
]
site_auths.add_group(*reportable_codenames, name=REPORTABLE_SUPER)
site_auths.add_group(
    *[code for code in reportable_codenames if "view" in code], name=REPORTABLE_VIEW
)

site_auths.update_role(REPORTABLE_VIEW, name=CLINICIAN_ROLE)
site_auths.update_role(REPORTABLE_VIEW, name=NURSE_ROLE)
site_auths.update_role(REPORTABLE_VIEW, name=AUDITOR_ROLE)
