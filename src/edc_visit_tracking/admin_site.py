from django.contrib.admin import AdminSite


class EdcVisitTrackingAdminSite(AdminSite):
    site_header = "Edc Visit Tracking"
    site_title = "Edc Visit Tracking"
    index_title = "Edc Visit Tracking Administration"
    site_url = "/administration/"


edc_visit_tracking_admin = EdcVisitTrackingAdminSite(name="edc_visit_tracking_admin")
edc_visit_tracking_admin.disable_action("delete_selected")
