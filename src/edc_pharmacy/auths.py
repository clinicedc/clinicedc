from edc_auth.site_auths import site_auths

from .auth_objects import (
    PHARMACIST_ROLE,
    PHARMACY,
    PHARMACY_AUDITOR_ROLE,
    PHARMACY_VIEW,
    PRESCRIBER,
    PRESCRIBER_ROLE,
    SITE_PHARMACIST_ROLE,
    pharmacy_codenames,
    prescriber_codenames,
)

site_auths.add_group(*pharmacy_codenames, name=PHARMACY_VIEW, view_only=True)
site_auths.add_group(*pharmacy_codenames, name=PHARMACY, no_delete=False)
site_auths.add_group(*prescriber_codenames, name=PRESCRIBER, no_delete=False)

site_auths.add_role(PHARMACY, name=PHARMACIST_ROLE)
site_auths.add_role(PHARMACY, name=SITE_PHARMACIST_ROLE)
site_auths.add_role(PRESCRIBER, name=PRESCRIBER_ROLE)
site_auths.add_role(PHARMACY_VIEW, name=PHARMACY_AUDITOR_ROLE)
