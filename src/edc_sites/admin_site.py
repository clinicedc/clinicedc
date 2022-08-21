from edc_model_admin.admin_site import EdcAdminSite

from .apps import AppConfig

edc_sites_admin = EdcAdminSite(name="edc_sites_admin", app_label=AppConfig.name)
