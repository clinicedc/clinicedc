from django.conf import settings
from edc_auth.auth_objects import AUDITOR_ROLE, CLINICIAN_ROLE, CLINICIAN_SUPER_ROLE
from edc_auth.site_auths import site_auths

from .auth_objects import (
    PROTOCOL_INCIDENT_VIEW,
    PROTOCOL_VIOLATION,
    PROTOCOL_VIOLATION_VIEW,
    protocol_incident_codenames,
    protocol_incident_view_codenames,
    protocol_violation_codenames,
    protocol_violation_view_codenames,
)
from .constants import PROTOCOL_DEVIATION_VIOLATION, PROTOCOL_INCIDENT

incident_type = getattr(settings, "EDC_PROTOCOL_VIOLATION_TYPE", PROTOCOL_DEVIATION_VIOLATION)

site_auths.add_group(*protocol_violation_codenames, name=PROTOCOL_VIOLATION)
site_auths.add_group(*protocol_violation_view_codenames, name=PROTOCOL_VIOLATION_VIEW)
site_auths.add_group(*protocol_incident_codenames, name=PROTOCOL_INCIDENT)
site_auths.add_group(*protocol_incident_view_codenames, name=PROTOCOL_INCIDENT_VIEW)

if incident_type == PROTOCOL_DEVIATION_VIOLATION:
    site_auths.update_role(PROTOCOL_VIOLATION, name=CLINICIAN_ROLE)
    site_auths.update_role(PROTOCOL_VIOLATION, name=CLINICIAN_SUPER_ROLE)
    site_auths.update_role(PROTOCOL_VIOLATION_VIEW, name=AUDITOR_ROLE)
elif incident_type == PROTOCOL_INCIDENT:
    site_auths.update_role(PROTOCOL_INCIDENT, name=CLINICIAN_ROLE)
    site_auths.update_role(PROTOCOL_INCIDENT, name=CLINICIAN_SUPER_ROLE)
    site_auths.update_role(PROTOCOL_INCIDENT_VIEW, name=AUDITOR_ROLE)
else:
    raise ValueError(
        "Invalid value for settings.EDC_PROTOCOL_VIOLATION_TYPE. "
        f"Expected `{PROTOCOL_INCIDENT}` or `{PROTOCOL_DEVIATION_VIOLATION}`. "
        f"Got {incident_type}."
    )
