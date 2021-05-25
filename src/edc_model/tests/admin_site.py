from django.contrib.admin import AdminSite, ModelAdmin, register

from .models import BasicModel


class EdcModelAdminSite(AdminSite):
    site_header = "EdcModel"
    site_title = "EdcModel"
    index_title = "EdcModel Administration"
    site_url = "/administration/"


edc_model_admin = EdcModelAdminSite(name="edc_model_admin")


@register(BasicModel, site=edc_model_admin)
class BasicModelAdmin(ModelAdmin):
    pass
