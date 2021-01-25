from edc_model_admin.admin_site import EdcAdminSite


class AdminSite(EdcAdminSite):
    site_header = "Edc Visit Tracking"
    site_title = "Edc Visit Tracking"
    index_title = "Edc Visit Tracking Administration"


edc_visit_tracking_admin = AdminSite(name="edc_visit_tracking_admin")
