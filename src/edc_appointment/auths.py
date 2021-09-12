from edc_auth.default_group_names import AUDITOR, CLINIC, EXPORT
from edc_auth.site_auths import site_auths

site_auths.update_group(
    "edc_appointment.view_appointment",
    "edc_appointment.view_historicalappointment",
    name=AUDITOR,
)

site_auths.update_group(
    "edc_appointment.add_appointment",
    "edc_appointment.change_appointment",
    "edc_appointment.view_appointment",
    "edc_appointment.view_historicalappointment",
    name=CLINIC,
)

site_auths.update_group(
    "edc_appointment.export_appointment",
    # "edc_appointment.export_historicalappointment",
    name=EXPORT,
)
