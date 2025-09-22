from django.apps import apps as django_apps

from edc_auth.constants import (
    ADMINISTRATION,
    AUDITOR_ROLE,
    CLINICIAN_ROLE,
    EVERYONE,
    NURSE_ROLE,
    PII_VIEW,
)
from edc_auth.site_auths import site_auths
from edc_export.constants import EXPORT

from .auth_objects import (
    LAB,
    LAB_TECHNICIAN_ROLE,
    LAB_VIEW,
    lab_codenames,
    lab_view_codenames,
)


def update_site_auths():
    site_auths.add_group(*lab_codenames, name=LAB)
    site_auths.add_group(*lab_view_codenames, name=LAB_VIEW)

    if django_apps.is_installed("edc_export"):
        site_auths.update_group(
            "edc_lab.export_aliquot",
            "edc_lab.export_box",
            "edc_lab.export_boxitem",
            "edc_lab.export_boxtype",
            "edc_lab.export_order",
            "edc_lab.export_panel",
            "edc_lab.export_result",
            "edc_lab.export_resultitem",
            name=EXPORT,
        )

    site_auths.add_role(ADMINISTRATION, EVERYONE, LAB, PII_VIEW, name=LAB_TECHNICIAN_ROLE)
    site_auths.update_role(LAB, name=CLINICIAN_ROLE)
    site_auths.update_role(LAB, name=NURSE_ROLE)
    site_auths.update_role(LAB_VIEW, name=AUDITOR_ROLE)


update_site_auths()
