from edc_auth.site_auths import site_auths

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
