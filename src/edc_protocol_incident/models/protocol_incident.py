from edc_action_item.managers import (
    ActionIdentifierModelManager,
    ActionIdentifierSiteManager,
)
from edc_action_item.models import ActionModelMixin
from edc_identifier.model_mixins import NonUniqueSubjectIdentifierFieldMixin
from edc_model.models import BaseUuidModel
from edc_sites.models import SiteModelMixin

from ..constants import PROTOCOL_INCIDENT_ACTION
from ..model_mixins import ProtocolIncidentModelMixin


class ProtocolIncident(
    ProtocolIncidentModelMixin,
    NonUniqueSubjectIdentifierFieldMixin,
    SiteModelMixin,
    ActionModelMixin,
    BaseUuidModel,
):
    action_name = PROTOCOL_INCIDENT_ACTION
    on_site = ActionIdentifierSiteManager()
    objects = ActionIdentifierModelManager()

    def natural_key(self):
        return (self.action_identifier,)  # noqa

    class Meta(ProtocolIncidentModelMixin.Meta, BaseUuidModel.Meta):
        pass
        # db_table = "edc_protocol_incident_protocolincident"
