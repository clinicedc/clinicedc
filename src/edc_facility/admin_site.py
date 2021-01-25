from edc_model_admin.admin_site import EdcAdminSite


class AdminSite(EdcAdminSite):
    site_header = "Edc Facility"
    site_title = "Edc Facility"
    index_title = "Edc Facility Administration"


edc_facility_admin = AdminSite(name="edc_facility_admin")
