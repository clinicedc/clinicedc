from edc_model_admin.admin_site import EdcAdminSite


class AdminSite(EdcAdminSite):
    site_title = "Edc Off-study"
    site_header = "Edc Off-study"
    index_title = "Edc Off-study"


edc_offstudy_admin = AdminSite(name="edc_offstudy_admin")
