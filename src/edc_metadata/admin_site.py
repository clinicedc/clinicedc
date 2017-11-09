from django.contrib.admin.sites import AdminSite


class EdcMetaDataAdminSite(AdminSite):
    site_header = 'Edc Metadata'
    site_title = 'Edc Metadata'
    index_title = 'Edc Metadata Administration'
    site_url = '/administration/'


edc_metadata_admin = EdcMetaDataAdminSite(name='edc_metadata_admin')
