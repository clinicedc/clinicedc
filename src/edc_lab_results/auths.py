from django.apps import apps as django_apps

from edc_auth.constants import (
    AUDITOR_ROLE,
    CLINICIAN_ROLE,
    NURSE_ROLE,
)
from edc_auth.site_auths import site_auths
from edc_export.constants import EXPORT

from .auth_objects import (
    LAB_RESULTS,
    lab_results_codenames,
)


def update_site_auths():
    site_auths.add_group(*lab_results_codenames, name=LAB_RESULTS)

    if django_apps.is_installed("edc_export"):
        site_auths.update_group(
            "edc_lab_results.export_result",
            "edc_lab_results.export_investigationmapping",
            name=EXPORT,
        )

    site_auths.update_role(LAB_RESULTS, name=AUDITOR_ROLE)
    site_auths.update_role(LAB_RESULTS, name=CLINICIAN_ROLE)
    site_auths.update_role(LAB_RESULTS, name=NURSE_ROLE)


update_site_auths()
