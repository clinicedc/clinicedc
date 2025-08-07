from edc_model_admin.admin_site import EdcAdminSite

from .apps import AppConfig

demo_consent_admin = EdcAdminSite(name="demo_consent_admin", app_label=AppConfig.name)
