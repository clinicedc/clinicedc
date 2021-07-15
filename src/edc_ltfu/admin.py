from django.contrib import admin
from edc_model_admin import SimpleHistoryAdmin
from edc_model_admin.dashboard import ModelAdminSubjectDashboardMixin

from .admin_site import edc_ltfu_admin
from .modeladmin_mixin import LtfuModelAdminMixin
from .models import Ltfu


@admin.register(Ltfu, site=edc_ltfu_admin)
class LtfuAdmin(LtfuModelAdminMixin, ModelAdminSubjectDashboardMixin, SimpleHistoryAdmin):
    pass
