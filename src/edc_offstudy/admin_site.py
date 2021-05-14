from edc_model_admin.admin_site import EdcAdminSite

from .apps import AppConfig

edc_offstudy_admin = EdcAdminSite(name="edc_offstudy_admin", app_label=AppConfig.name)
