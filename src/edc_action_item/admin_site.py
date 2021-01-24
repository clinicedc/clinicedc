from edc_model_admin.admin_site import EdcAdminSite


class AdminSite(EdcAdminSite):
    site_title = "Edc Action Item"
    site_header = "Edc Action Item"
    index_title = "Edc Action Item"


edc_action_item_admin = AdminSite(name="edc_action_item_admin")
