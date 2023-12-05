from edc_list_data.model_mixins import ListModelMixin


class ActionsRequired(ListModelMixin):
    class Meta(ListModelMixin.Meta):
        verbose_name = "Actions Required"
        verbose_name_plural = "Actions Required"


class ProtocolViolations(ListModelMixin):
    class Meta(ListModelMixin.Meta):
        verbose_name = "Protocol Violations"
        verbose_name_plural = "Protocol Violations"


class ProtocolIncidents(ListModelMixin):
    class Meta(ListModelMixin.Meta):
        verbose_name = "Protocol Incidents"
        verbose_name_plural = "Protocol Incidents"
