from edc_model_admin.admin_site import EdcAdminSite

from .apps import AppConfig

edc_locator_admin = EdcAdminSite(name="edc_locator_admin", app_label=AppConfig.name)
