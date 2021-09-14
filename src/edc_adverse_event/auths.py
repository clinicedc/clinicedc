from edc_auth.auth_objects import AUDITOR_ROLE, CLINICIAN_ROLE, NURSE_ROLE, REVIEW
from edc_auth.site_auths import site_auths
from edc_data_manager.auth_objects import DATA_MANAGER_ROLE, SITE_DATA_MANAGER_ROLE
from edc_export.auth_objects import EXPORT

from edc_adverse_event.auth_objects import (
    AE_ROLE,
    ae_navbar_tuples,
    tmg_dashboard_tuples,
    tmg_navbar_tuples,
)

from .auth_objects import (
    AE,
    AE_REVIEW,
    TMG,
    TMG_REVIEW,
    TMG_ROLE,
    ae_codenames,
    ae_dashboard_tuples,
    ae_view_codenames,
    tmg_codenames,
    tmg_view_codenames,
)

# groups
site_auths.add_group(
    *ae_codenames,
    *[c[0] for c in ae_dashboard_tuples],
    *[c[0] for c in ae_navbar_tuples],
    name=AE,
)
site_auths.add_group(
    *ae_view_codenames,
    *[c[0] for c in ae_dashboard_tuples],
    *[c[0] for c in ae_navbar_tuples],
    name=AE_REVIEW,
)
site_auths.add_group(
    *tmg_codenames,
    *[c[0] for c in tmg_dashboard_tuples],
    *[c[0] for c in tmg_navbar_tuples],
    name=TMG,
)
site_auths.add_group(
    *tmg_view_codenames,
    *[c[0] for c in tmg_dashboard_tuples],
    *[c[0] for c in tmg_navbar_tuples],
    name=TMG_REVIEW,
)
site_auths.update_group(
    "edc_adverse_event.export_aeclassification",
    "edc_adverse_event.export_causeofdeath",
    "edc_adverse_event.export_saereason",
    name=EXPORT,
)
# add roles
site_auths.add_role(REVIEW, AE, name=AE_ROLE)
site_auths.add_role(REVIEW, AE_REVIEW, TMG, name=TMG_ROLE)

# update roles
site_auths.update_role(AE, name=CLINICIAN_ROLE)
site_auths.update_role(AE, name=NURSE_ROLE)
site_auths.update_role(AE_REVIEW, TMG_REVIEW, name=AUDITOR_ROLE)
site_auths.update_role(AE, TMG, name=DATA_MANAGER_ROLE)
site_auths.update_role(AE_REVIEW, TMG_REVIEW, name=SITE_DATA_MANAGER_ROLE)

# custom perms
site_auths.add_custom_permissions_tuples(
    model="edc_dashboard.dashboard", codename_tuples=ae_dashboard_tuples
)
site_auths.add_custom_permissions_tuples(
    model="edc_navbar.navbar", codename_tuples=ae_navbar_tuples
)
site_auths.add_custom_permissions_tuples(
    model="edc_dashboard.dashboard", codename_tuples=tmg_dashboard_tuples
)
site_auths.add_custom_permissions_tuples(
    model="edc_navbar.navbar", codename_tuples=tmg_navbar_tuples
)
