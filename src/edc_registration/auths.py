from edc_auth.auth_objects import PII
from edc_auth.site_auths import site_auths
from edc_export.auth_objects import EXPORT

site_auths.update_group("edc_registration.export_registeredsubject", name=EXPORT)
site_auths.update_group(
    "edc_registration.display_dob",
    "edc_registration.display_firstname",
    "edc_registration.display_identity",
    "edc_registration.display_initials",
    "edc_registration.display_lastname",
    "edc_registration.view_historicalregisteredsubject",
    "edc_registration.view_registeredsubject",
    name=PII,
)
