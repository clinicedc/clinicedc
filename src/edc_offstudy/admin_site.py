from django.contrib.admin import AdminSite as DjangoAdminSite


class AdminSite(DjangoAdminSite):
    site_title = "Edc Off-study"
    site_header = "Edc Off-study"
    index_title = "Edc Off-study"
    site_url = "/administration/"


edc_offstudy_admin = AdminSite(name="edc_offstudy_admin")
edc_offstudy_admin.disable_action("delete_selected")
