from edc_model_admin.admin_site import EdcAdminSite


class AdminSite(EdcAdminSite):
    site_title = "Edc Locator"
    site_header = "Edc Locator"
    index_title = "Edc Locator"


edc_locator_admin = AdminSite(name="edc_locator_admin")
