from django.apps import apps as django_apps

from edc_auth.site_auths import site_auths
from edc_export.constants import EXPORT


def update_site_auths():
    if django_apps.is_installed("edc_export"):
        site_auths.update_group(
            "edc_metadata.export_crfmetadata",
            "edc_metadata.export_requisitionmetadata",
            name=EXPORT,
        )


update_site_auths()
