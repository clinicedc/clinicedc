from django.contrib.admin import register, ModelAdmin

from .admin_site import edc_model_admin
from .models import TestBaseModel


@register(TestBaseModel, site=edc_model_admin)
class TestBaseModelAdmin(ModelAdmin):
    pass
