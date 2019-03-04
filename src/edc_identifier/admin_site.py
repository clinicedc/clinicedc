from django.contrib.admin.sites import AdminSite


class EdcIdentifierAdminSite(AdminSite):
    site_header = "Edc Identifier"
    site_title = "Edc Identifier"
    index_title = "Edc Identifier"
    site_url = "/administration/"


edc_identifier_admin = EdcIdentifierAdminSite(name="edc_identifier_admin")
edc_identifier_admin.disable_action("delete_selected")
