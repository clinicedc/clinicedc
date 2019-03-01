from django.contrib.admin import AdminSite


class EdcModelAdminSite(AdminSite):
    site_header = "EdcModel"
    site_title = "EdcModel"
    index_title = "EdcModel Administration"
    site_url = "/administration/"


edc_model_admin = EdcModelAdminSite(name="edc_model_admin")
