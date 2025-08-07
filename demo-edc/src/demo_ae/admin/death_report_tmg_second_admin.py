from django.contrib import admin

from edc_adverse_event.forms import DeathReportTmgSecondForm
from edc_adverse_event.modeladmin_mixins import DeathReportTmgModelAdminMixin
from edc_model_admin.history import SimpleHistoryAdmin
from edc_sites.admin import SiteModelAdminMixin

from ..admin_site import demo_ae_admin
from ..models import DeathReportTmgSecond


@admin.register(DeathReportTmgSecond, site=demo_ae_admin)
class DeathReportTmgSecondAdmin(
    SiteModelAdminMixin, DeathReportTmgModelAdminMixin, SimpleHistoryAdmin
):
    form = DeathReportTmgSecondForm
