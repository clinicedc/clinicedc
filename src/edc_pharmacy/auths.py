from edc_auth.site_auths import site_auths
from edc_auth.utils import remove_default_model_permissions_from_edc_permissions
from edc_pylabels.auth_objects import PYLABELS

from .auth_objects import (
    PHARMACIST_ROLE,
    PHARMACY,
    PHARMACY_AUDITOR_ROLE,
    PHARMACY_PRESCRIBER,
    PHARMACY_PRESCRIBER_ROLE,
    PHARMACY_SITE,
    PHARMACY_SUPER_ROLE,
    PHARMACY_VIEW,
    SITE_PHARMACIST_ROLE,
    navbar_tuples,
    pharmacy_codenames,
    pharmacy_site_codenames,
    prescriber_codenames,
)

site_auths.add_post_update_func(
    "edc_pharmacy", remove_default_model_permissions_from_edc_permissions
)
site_auths.add_custom_permissions_tuples(
    model="edc_pharmacy.edcpermissions", codename_tuples=navbar_tuples
)

site_auths.add_group(*pharmacy_codenames, name=PHARMACY_VIEW, view_only=True)
site_auths.add_group(*prescriber_codenames, name=PHARMACY_PRESCRIBER, no_delete=True)
site_auths.add_group(*pharmacy_site_codenames, name=PHARMACY_SITE, no_delete=False)
site_auths.add_group(*pharmacy_codenames, name=PHARMACY, no_delete=False)


site_auths.add_role(PHARMACY_VIEW, name=PHARMACY_AUDITOR_ROLE)
site_auths.add_role(PHARMACY_PRESCRIBER, name=PHARMACY_PRESCRIBER_ROLE)
site_auths.add_role(PHARMACY_SITE, PYLABELS, name=SITE_PHARMACIST_ROLE)
site_auths.add_role(PHARMACY, PYLABELS, name=PHARMACIST_ROLE)
site_auths.add_role(PHARMACY, name=PHARMACY_SUPER_ROLE)
