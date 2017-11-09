from django.contrib.admin import AdminSite


class EdcAppointmentAdminSite(AdminSite):
    site_header = 'Appointments'
    site_title = 'Appointments'
    index_title = 'Appointments Administration'
    site_url = '/administration/'


edc_appointment_admin = EdcAppointmentAdminSite(
    name='edc_appointment_admin')
