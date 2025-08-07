from django.contrib import admin

from edc_adverse_event.forms import AeInitialForm
from edc_adverse_event.modeladmin_mixins import AeInitialModelAdminMixin
from edc_model_admin.history import SimpleHistoryAdmin
from edc_sites.admin import SiteModelAdminMixin

from ..admin_site import demo_ae_admin
from ..models import AeInitial


@admin.register(AeInitial, site=demo_ae_admin)
class AeInitialAdmin(SiteModelAdminMixin, AeInitialModelAdminMixin, SimpleHistoryAdmin):
    form = AeInitialForm
