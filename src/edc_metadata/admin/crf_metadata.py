from django.contrib import admin
from edc_model_admin.dashboard import ModelAdminSubjectDashboardMixin
from edc_model_admin.model_admin_simple_history import SimpleHistoryAdmin

from ..admin_site import edc_metadata_admin
from ..modeladmin_mixins import CrfMetadataAdminMixin
from ..models import CrfMetadata


@admin.register(CrfMetadata, site=edc_metadata_admin)
class CrfMetadataAdmin(
    CrfMetadataAdminMixin, ModelAdminSubjectDashboardMixin, SimpleHistoryAdmin
):

    pass
