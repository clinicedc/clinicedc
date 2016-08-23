from django.contrib.admin import AdminSite


class EdcLabAdminSite(AdminSite):
    site_header = 'Edc Lab'
    site_title = 'Edc Lab'
    index_title = 'Edc Lab Administration'
    site_url = '/edc-lab/'
edc_lab_admin = EdcLabAdminSite(name='edc_lab_admin')
