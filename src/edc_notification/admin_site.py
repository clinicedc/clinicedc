from django.contrib.admin import AdminSite as DjangoAdminSite


class AdminSite(DjangoAdminSite):
    site_title = 'Edc Notification'
    site_header = 'Edc Notification'
    index_title = 'Edc Notification'
    site_url = '/administration/'


edc_notification_admin = AdminSite(name='edc_notification_admin')
