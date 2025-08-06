from django.contrib import admin
from edc_model_admin.mixins import AddressModelAdminMixin

from ..admin_site import edc_lab_admin
from ..models import Consignee
from .base_model_admin import BaseModelAdmin


@admin.register(Consignee, site=edc_lab_admin)
class ConsigneeAdmin(BaseModelAdmin, AddressModelAdminMixin, admin.ModelAdmin):
    pass
