from edc_model_admin.admin_site import EdcAdminSite


class AdminSite(EdcAdminSite):
    site_title = "Edc Notification"
    site_header = "Edc Notification"
    index_title = "Edc Notification"


edc_notification_admin = AdminSite(name="edc_notification_admin")
