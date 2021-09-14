from edc_auth.auth_objects import (
    AUDITOR_ROLE,
    CLINICIAN_ROLE,
    CLINICIAN_SUPER_ROLE,
    NURSE_ROLE,
)
from edc_auth.site_auths import site_auths
from edc_data_manager.auth_objects import DATA_MANAGER_ROLE
from edc_export.auth_objects import EXPORT

from .auth_objects import APPOINTMENT, APPOINTMENT_VIEW

site_auths.add_group(
    "edc_appointment.view_appointment",
    "edc_appointment.view_historicalappointment",
    name=APPOINTMENT_VIEW,
)

site_auths.add_group(
    "edc_appointment.add_appointment",
    "edc_appointment.change_appointment",
    "edc_appointment.view_appointment",
    "edc_appointment.view_historicalappointment",
    name=APPOINTMENT,
)

site_auths.update_group(
    "edc_appointment.export_appointment",
    name=EXPORT,
)

site_auths.update_role(APPOINTMENT, name=CLINICIAN_ROLE)
site_auths.update_role(APPOINTMENT, name=CLINICIAN_SUPER_ROLE)
site_auths.update_role(APPOINTMENT, name=DATA_MANAGER_ROLE)
site_auths.update_role(APPOINTMENT, name=NURSE_ROLE)
site_auths.update_role(APPOINTMENT_VIEW, name=AUDITOR_ROLE)
