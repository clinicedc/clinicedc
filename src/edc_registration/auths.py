from django.apps import apps as django_apps

from edc_auth.constants import PII, PII_VIEW
from edc_auth.site_auths import site_auths
from edc_export.constants import EXPORT


def update_site_auths() -> None:
    if django_apps.is_installed("edc_export"):
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

    site_auths.update_group(
        "edc_registration.display_dob",
        "edc_registration.display_firstname",
        "edc_registration.display_identity",
        "edc_registration.display_initials",
        "edc_registration.display_lastname",
        "edc_registration.view_historicalregisteredsubject",
        "edc_registration.view_registeredsubject",
        name=PII_VIEW,
    )
    site_auths.add_pii_model("edc_registration.registeredsubject")


update_site_auths()
