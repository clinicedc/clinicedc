from edc_model_admin.admin_site import EdcAdminSite


class AdminSite(EdcAdminSite):
    site_header = "Edc Lab"
    site_title = "Edc Lab"
    index_title = "Edc Lab Administration"


edc_lab_admin = AdminSite(name="edc_lab_admin")
