from edc_model_admin.admin_site import EdcAdminSite

from .apps import AppConfig

edc_consent_admin = EdcAdminSite(name="edc_consent_admin", app_label=AppConfig.name)
