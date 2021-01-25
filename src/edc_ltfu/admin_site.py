from edc_model_admin.admin_site import EdcAdminSite


class AdminSite(EdcAdminSite):
    site_title = "Edc Loss to Follow up"
    site_header = "Edc Loss to Follow up"
    index_title = "Edc Loss to Follow up"


edc_ltfu_admin = AdminSite(name="edc_ltfu_admin")
