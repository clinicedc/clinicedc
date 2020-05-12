from django.contrib.admin.sites import AdminSite as DjangoAdminSite


class AdminSite(DjangoAdminSite):
    site_header = "Edc CRF"
    site_title = "Edc CRF"
    index_title = "Edc CRF Administration"
    site_url = "/administration/"


edc_crf_admin = AdminSite(name="edc_crf_admin")
edc_crf_admin.disable_action("delete_selected")
