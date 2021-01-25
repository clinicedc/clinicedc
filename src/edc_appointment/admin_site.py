from edc_model_admin.admin_site import EdcAdminSite


class AdminSite(EdcAdminSite):
    site_header = "Appointments"
    site_title = "Appointments"
    index_title = "Appointments Administration"
    site_url = "/administration/"


edc_appointment_admin = AdminSite(name="edc_appointment_admin")
