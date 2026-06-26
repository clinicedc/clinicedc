from django.apps import apps as django_apps

from edc_auth.constants import CLINIC
from edc_auth.site_auths import site_auths
from edc_data_manager.auth_objects import DATA_MANAGER
from edc_export.constants import EXPORT

codenames = [
    "edc_metadata.add_crfmetadatamissing",
    "edc_metadata.change_crfmetadatamissing",
    "edc_metadata.delete_crfmetadatamissing",
    "edc_metadata.view_crfmetadatamissing",
    "edc_metadata.view_crfmetadata",
    "edc_metadata.add_requisitionmetadatamissing",
    "edc_metadata.change_requisitionmetadatamissing",
    "edc_metadata.delete_requisitionmetadatamissing",
    "edc_metadata.view_requisitionmetadatamissing",
    "edc_metadata.view_requisitionmetadata",
    "edc_metadata.view_datamissingreason",
    "edc_metadata.view_reviewfilter",
]


def update_site_auths():
    if django_apps.is_installed("edc_export"):
        site_auths.update_group(
            "edc_metadata.export_crfmetadata",
            "edc_metadata.export_requisitionmetadata",
            name=EXPORT,
        )
    site_auths.update_group(*codenames, name=DATA_MANAGER)
    site_auths.update_group(*codenames, name=CLINIC)


update_site_auths()
