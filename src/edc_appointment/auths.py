from edc_auth.auth_objects import (
    AUDITOR_ROLE,
    CLINICIAN_ROLE,
    CLINICIAN_SUPER_ROLE,
    NURSE_ROLE,
)
from edc_auth.site_auths import site_auths

from .auth_objects import APPOINTMENT, APPOINTMENT_EXPORT, APPOINTMENT_VIEW, codenames

site_auths.add_group(*codenames, name=APPOINTMENT_VIEW, view_only=True)

site_auths.add_group(*codenames, name=APPOINTMENT)

site_auths.add_group(
    "edc_appointment.export_appointment",
    name=APPOINTMENT_EXPORT,
)


site_auths.update_role(APPOINTMENT, name=CLINICIAN_ROLE)
site_auths.update_role(APPOINTMENT, name=NURSE_ROLE)
site_auths.update_role(APPOINTMENT_VIEW, name=AUDITOR_ROLE)
site_auths.update_role(APPOINTMENT, name=CLINICIAN_SUPER_ROLE)
