from edc_auth.auth_objects import (
    AUDITOR_ROLE,
    CLINICIAN_ROLE,
    CLINICIAN_SUPER_ROLE,
    NURSE_ROLE,
)
from edc_auth.site_auths import site_auths
from edc_auth.utils import remove_default_model_permissions_from_edc_permissions

from .auth_objects import (
    AE,
    AE_REVIEW,
    AE_ROLE,
    AE_SUPER,
    TMG,
    TMG_REVIEW,
    TMG_ROLE,
    ae_codenames,
    ae_dashboard_tuples,
    ae_navbar_tuples,
    tmg_codenames,
    tmg_dashboard_tuples,
    tmg_navbar_tuples,
)

site_auths.add_post_update_func(
    "edc_adverse_event", remove_default_model_permissions_from_edc_permissions
)

permissions_model = "edc_adverse_event.edcpermissions"

# custom perms
site_auths.add_custom_permissions_tuples(
    model=permissions_model, codename_tuples=ae_dashboard_tuples
)
site_auths.add_custom_permissions_tuples(
    model=permissions_model, codename_tuples=tmg_dashboard_tuples
)

site_auths.add_custom_permissions_tuples(
    model=permissions_model, codename_tuples=tmg_navbar_tuples
)
site_auths.add_custom_permissions_tuples(
    model=permissions_model, codename_tuples=ae_navbar_tuples
)

# groups
site_auths.add_group(*ae_codenames, name=AE, no_delete=True)
site_auths.update_group(
    *[c[0] for c in ae_dashboard_tuples], *[c[0] for c in ae_navbar_tuples], name=AE
)

site_auths.add_group(*ae_codenames, name=AE_SUPER)
site_auths.update_group(
    *[c[0] for c in ae_dashboard_tuples], *[c[0] for c in ae_navbar_tuples], name=AE_SUPER
)

site_auths.add_group(*ae_codenames, name=AE_REVIEW, view_only=True)
site_auths.update_group(
    *[c[0] for c in ae_dashboard_tuples], *[c[0] for c in ae_navbar_tuples], name=AE_REVIEW
)

site_auths.add_group(*tmg_codenames, name=TMG)
site_auths.update_group(
    *[c[0] for c in tmg_dashboard_tuples], *[c[0] for c in tmg_navbar_tuples], name=TMG
)

site_auths.add_group(*tmg_codenames, name=TMG_REVIEW, view_only=True)
site_auths.update_group(
    *[c[0] for c in tmg_dashboard_tuples], *[c[0] for c in tmg_navbar_tuples], name=TMG_REVIEW
)

# add roles
site_auths.add_role(AE, name=AE_ROLE)
site_auths.add_role(AE_REVIEW, TMG, name=TMG_ROLE)


site_auths.update_role(AE, name=CLINICIAN_ROLE)
site_auths.update_role(AE, name=NURSE_ROLE)
site_auths.update_role(AE_REVIEW, TMG_REVIEW, name=AUDITOR_ROLE)
site_auths.update_role(AE_SUPER, name=CLINICIAN_SUPER_ROLE)
