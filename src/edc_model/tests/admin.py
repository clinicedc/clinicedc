from django.contrib.admin import register, ModelAdmin

from .admin_site import edc_model_admin
from .models import BasicModel


@register(BasicModel, site=edc_model_admin)
class BasicModelAdmin(ModelAdmin):
    pass
