from django.contrib.admin import AdminSite


class EdcDataManagerAdminSite(AdminSite):
    site_title = "Data Management"
    site_header = "Data Management"
    index_title = "Data Management"
    site_url = "/administration/"


edc_data_manager_admin = EdcDataManagerAdminSite(name="edc_data_manager_admin")
# edc_data_manager_admin.disable_action("delete_selected")
