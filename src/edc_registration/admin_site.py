from django.contrib.admin import AdminSite


class EdcRegistrationAdminSite(AdminSite):
    site_header = 'Registration'
    site_title = 'Registration'
    index_title = 'Registration Administration'
    site_url = '/administration/'


edc_registration_admin = EdcRegistrationAdminSite(
    name='edc_registration_admin')
