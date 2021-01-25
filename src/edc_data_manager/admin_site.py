from edc_model_admin.admin_site import EdcAdminSite


class AdminSite(EdcAdminSite):
    site_title = "Data Management"
    site_header = "Data Management"
    index_title = "Data Management"
    site_url = "/administration/"


edc_data_manager_admin = AdminSite(name="edc_data_manager_admin")
# edc_data_manager_admin.disable_action("delete_selected")
