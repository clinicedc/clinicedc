from edc_list_data.model_mixins import ListModelMixin


class ActionsRequired(ListModelMixin):
    class Meta(ListModelMixin.Meta):
        verbose_name = "Actions Required"
        verbose_name_plural = "Actions Required"
        # db_table = "edc_protocol_incident_actionsrequired"


class ProtocolViolations(ListModelMixin):
    class Meta(ListModelMixin.Meta):
        verbose_name = "Protocol Violations"
        verbose_name_plural = "Protocol Violations"
        # db_table = "edc_protocol_incident_protocoldeviationviolations"


class ProtocolIncidents(ListModelMixin):
    class Meta(ListModelMixin.Meta):
        verbose_name = "Protocol Incidents"
        verbose_name_plural = "Protocol Incidents"
        # db_table = "edc_protocol_incident_protocolincidents"
