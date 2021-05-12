from edc_model_admin.admin_site import EdcAdminSite

from .apps import AppConfig

edc_auth_admin = EdcAdminSite(name="edc_auth_admin", app_label=AppConfig.name)
