from django.contrib.admin import AdminSite


class EdcExportAdminSite(AdminSite):
    site_header = 'Edc Export'
    site_title = 'Edc Export'
    index_title = 'Edc Export Administration'
    site_url = '/'


edc_export_admin = EdcExportAdminSite(name='edc_export_admin')
