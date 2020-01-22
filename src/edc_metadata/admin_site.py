from django.contrib.admin.sites import AdminSite as DjangoAdminSite


class AdminSite(DjangoAdminSite):
    site_header = "Edc Metadata"
    site_title = "Edc Metadata"
    index_title = "Edc Metadata Administration"
    site_url = "/administration/"


edc_metadata_admin = AdminSite(name="edc_metadata_admin")
edc_metadata_admin.disable_action("delete_selected")
