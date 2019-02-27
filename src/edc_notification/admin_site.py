from django.contrib.admin import AdminSite as DjangoAdminSite


class AdminSite(DjangoAdminSite):
    site_title = "Edc Notification"
    site_header = "Edc Notification"
    index_title = "Edc Notification"
    site_url = "/administration/"


edc_notification_admin = AdminSite(name="edc_notification_admin")
edc_notification_admin.disable_action("delete_selected")
