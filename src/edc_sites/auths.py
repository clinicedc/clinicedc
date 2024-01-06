from edc_auth.site_auths import site_auths
from edc_auth.utils import remove_default_model_permissions_from_edc_permissions

site_auths.add_post_update_func(
    "edc_sites", remove_default_model_permissions_from_edc_permissions
)

view_auditallsites_codename = "view_auditallsites"
site_auths.add_custom_permissions_tuples(
    model="edc_sites.edcpermissions",
    codename_tuples=[
        (f"edc_sites.{view_auditallsites_codename}", "View all sites as auditor")
    ],
)
