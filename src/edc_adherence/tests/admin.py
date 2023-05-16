from django.contrib import admin
from django.contrib.admin import AdminSite as DjangoAdminSite
from edc_model_admin.dashboard import ModelAdminCrfDashboardMixin
from edc_model_admin.history import SimpleHistoryAdmin

from edc_adherence.model_admin_mixin import MedicationAdherenceAdminMixin

from .forms import MedicationAdherenceForm
from .models import MedicationAdherence


class CrfModelAdmin(ModelAdminCrfDashboardMixin, SimpleHistoryAdmin):
    pass


class AdminSite(DjangoAdminSite):
    pass


my_admin_site = AdminSite(name="my_admin_site")


@admin.register(MedicationAdherence)
class MedicationAdherenceAdmin(MedicationAdherenceAdminMixin, CrfModelAdmin):
    form = MedicationAdherenceForm
