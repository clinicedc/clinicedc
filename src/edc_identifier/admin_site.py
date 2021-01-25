from edc_model_admin.admin_site import EdcAdminSite


class AdminSite(EdcAdminSite):
    site_header = "Edc Identifier"
    site_title = "Edc Identifier"
    index_title = "Edc Identifier"


edc_identifier_admin = AdminSite(name="edc_identifier_admin")
