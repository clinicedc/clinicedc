from edc_model_admin.admin_site import EdcAdminSite


class AdminSite(EdcAdminSite):
    site_header = "Edc Export"
    site_title = "Edc Export"
    index_title = "Edc Export Administration"
    site_url = "/"


edc_export_admin = AdminSite(name="edc_export_admin")
