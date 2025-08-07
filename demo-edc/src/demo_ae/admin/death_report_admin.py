from django.contrib import admin

from edc_adverse_event.forms import DeathReportForm
from edc_adverse_event.modeladmin_mixins import DeathReportModelAdminMixin
from edc_model_admin.history import SimpleHistoryAdmin
from edc_sites.admin import SiteModelAdminMixin

from ..admin_site import demo_ae_admin
from ..models import DeathReport


@admin.register(DeathReport, site=demo_ae_admin)
class DeathReportAdmin(SiteModelAdminMixin, DeathReportModelAdminMixin, SimpleHistoryAdmin):
    form = DeathReportForm
