from edc_model_admin.admin_site import EdcAdminSite


class AdminSite(EdcAdminSite):
    site_header = "Edc Metadata"
    site_title = "Edc Metadata"
    index_title = "Edc Metadata Administration"


edc_metadata_admin = AdminSite(name="edc_metadata_admin")
