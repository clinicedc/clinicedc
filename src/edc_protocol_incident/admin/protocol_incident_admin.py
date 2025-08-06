from django.contrib import admin
from edc_model_admin.dashboard import ModelAdminSubjectDashboardMixin
from edc_model_admin.history import SimpleHistoryAdmin

from ..admin_site import edc_protocol_incident_admin
from ..forms import ProtocolIncidentForm
from ..models import ProtocolIncident


@admin.register(ProtocolIncident, site=edc_protocol_incident_admin)
class ProtocolIncidentAdmin(ModelAdminSubjectDashboardMixin, SimpleHistoryAdmin):
    form = ProtocolIncidentForm
