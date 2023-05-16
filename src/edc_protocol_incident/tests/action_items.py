from edc_protocol_incident.action_items import (
    ProtocolDeviationViolationAction as BaseProtocolDeviationViolationAction,
)
from edc_protocol_incident.action_items import (
    ProtocolIncidentAction as BaseProtocolIncidentAction,
)


class ProtocolDeviationViolationAction(BaseProtocolDeviationViolationAction):
    reference_model = "edc_protocol_incident.protocoldeviationviolation"
    admin_site_name = "edc_protocol_incident"


class ProtocolIncidentAction(BaseProtocolIncidentAction):
    reference_model = "edc_protocol_incident.protocolincident"
    admin_site_name = "edc_protocol_incident"
