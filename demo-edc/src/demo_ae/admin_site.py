from edc_model_admin.admin_site import EdcAdminSite

from .apps import AppConfig

demo_ae_admin = EdcAdminSite(name="demo_ae_admin", app_label=AppConfig.name)
