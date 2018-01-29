from django.contrib import admin

from ..admin_site import edc_lab_admin
from ..models import Order
from .base_model_admin import BaseModelAdmin


@admin.register(Order, site=edc_lab_admin)
class OrderAdmin(BaseModelAdmin, admin.ModelAdmin):
    pass
