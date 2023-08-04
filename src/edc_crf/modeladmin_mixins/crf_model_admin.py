from edc_model_admin.dashboard import ModelAdminCrfDashboardMixin
from edc_model_admin.history import SimpleHistoryAdmin
from edc_model_admin.mixins import ModelAdminProtectPiiMixin
from edc_sites.admin import SiteModelAdminMixin

from .crf_status_model_admin_mixin import CrfStatusModelAdminMixin


class CrfModelAdmin(
    ModelAdminProtectPiiMixin,  # must remain first
    SiteModelAdminMixin,
    CrfStatusModelAdminMixin,
    ModelAdminCrfDashboardMixin,
    SimpleHistoryAdmin,
):
    pass
