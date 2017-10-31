from django.contrib import admin

from ..admin_site import edc_pharma_admin
from ..forms import AppointmentForm, WorklistForm
from ..models import Appointment, WorkList
from .model_admin_mixin import ModelAdminMixin


@admin.register(Appointment, site=edc_pharma_admin)
class AppointmentAdmin(ModelAdminMixin, admin.ModelAdmin):

    form = AppointmentForm


@admin.register(WorkList, site=edc_pharma_admin)
class WorkListAdmin(ModelAdminMixin, admin.ModelAdmin):

    form = WorklistForm
