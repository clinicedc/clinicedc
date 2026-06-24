from django.apps import apps as django_apps

from edc_auth.constants import CLINIC
from edc_auth.site_auths import site_auths
from edc_data_manager.auth_objects import DATA_MANAGER
from edc_export.constants import EXPORT

# Permissions for the "data unavailable" flags. Site-scoping (clinic staff act
# only on their own site) is enforced in the view, not via these codenames.
unavailable_codenames = [
    "edc_metadata.add_crfmetadataunavailable",
    "edc_metadata.change_crfmetadataunavailable",
    "edc_metadata.delete_crfmetadataunavailable",
    "edc_metadata.view_crfmetadataunavailable",
    "edc_metadata.add_requisitionmetadataunavailable",
    "edc_metadata.change_requisitionmetadataunavailable",
    "edc_metadata.delete_requisitionmetadataunavailable",
    "edc_metadata.view_requisitionmetadataunavailable",
    "edc_metadata.view_dataunavailablereason",
]


def update_site_auths():
    if django_apps.is_installed("edc_export"):
        site_auths.update_group(
            "edc_metadata.export_crfmetadata",
            "edc_metadata.export_requisitionmetadata",
            name=EXPORT,
        )
    site_auths.update_group(*unavailable_codenames, name=DATA_MANAGER)
    site_auths.update_group(*unavailable_codenames, name=CLINIC)


update_site_auths()
