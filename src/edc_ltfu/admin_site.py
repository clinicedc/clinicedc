from django.contrib.admin import AdminSite as DjangoAdminSite


class AdminSite(DjangoAdminSite):
    site_title = "Edc Loss to Follow up"
    site_header = "Edc Loss to Follow up"
    index_title = "Edc Loss to Follow up"
    site_url = "/administration/"


edc_ltfu_admin = AdminSite(name="edc_ltfu_admin")
edc_ltfu_admin.disable_action("delete_selected")
