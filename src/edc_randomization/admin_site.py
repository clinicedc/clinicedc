from edc_model_admin.admin_site import EdcAdminSite


class AdminSite(EdcAdminSite):
    site_title = "Randomization"
    site_header = "Randomization"
    index_title = "Randomization"


edc_randomization_admin = AdminSite(name="edc_randomization_admin")
