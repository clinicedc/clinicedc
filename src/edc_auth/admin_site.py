from edc_model_admin.admin_site import EdcAdminSite


class AdminSite(EdcAdminSite):
    site_header = "Edc Authentication"
    site_title = "Edc Authentication"
    index_title = "Edc Authentication"


edc_auth_admin = AdminSite(name="edc_auth_admin")
