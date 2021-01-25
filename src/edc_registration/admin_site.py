from edc_model_admin.admin_site import EdcAdminSite


class AdminSite(EdcAdminSite):
    site_header = "Registration"
    site_title = "Registration"
    index_title = "Registration Administration"


edc_registration_admin = AdminSite(name="edc_registration_admin")
