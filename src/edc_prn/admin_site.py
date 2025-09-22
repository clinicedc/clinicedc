from edc_model_admin.admin_site import EdcAdminSite

from .apps import AppConfig

edc_prn_admin = EdcAdminSite(name="edc_prn_admin", app_label=AppConfig.name)
