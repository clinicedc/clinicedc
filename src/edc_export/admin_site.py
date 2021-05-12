from edc_model_admin.admin_site import EdcAdminSite

from .apps import AppConfig

edc_export_admin = EdcAdminSite(name="edc_export_admin", app_label=AppConfig.name)
