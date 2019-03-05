from django.contrib.admin import AdminSite as DjangoAdminSite


class AdminSite(DjangoAdminSite):
    site_title = "Edc Locator"
    site_header = "Edc Locator"
    index_title = "Edc Locator"
    site_url = "/administration/"


edc_locator_admin = AdminSite(name="edc_locator_admin")
edc_locator_admin.disable_action("delete_selected")
