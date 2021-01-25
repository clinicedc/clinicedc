from edc_model_admin.admin_site import EdcAdminSite


class AdminSite(EdcAdminSite):
    site_header = "Edc CRF"
    site_title = "Edc CRF"
    index_title = "Edc CRF Administration"
    site_url = "/administration/"


edc_crf_admin = AdminSite(name="edc_crf_admin")
