from django.contrib.admin import AdminSite as DjangoAdminSite


class AdminSite(DjangoAdminSite):

    site_title = 'EDC Pandas Utils'
    site_header = 'EDC Pandas Utils'
    index_title = 'EDC Pandas Utils'
    site_url = '/administration/'


edc_pdutils_admin = AdminSite(name='edc_pdutils_admin')
