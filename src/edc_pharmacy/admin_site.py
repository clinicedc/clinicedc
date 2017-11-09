from django.contrib.admin import AdminSite


class EdcPharmacyAdminSite(AdminSite):
    site_header = 'Edc Pharmacy'
    site_title = 'Edc Pharmacy'
    index_title = 'Edc Pharmacy Administration'
    site_url = '/administration/'


edc_pharmacy_admin = EdcPharmacyAdminSite(name='edc_pharmacy_admin')
