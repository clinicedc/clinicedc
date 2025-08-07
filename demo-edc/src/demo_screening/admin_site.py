from edc_model_admin.admin_site import EdcAdminSite

from .apps import AppConfig

demo_screening_admin = EdcAdminSite(name="demo_screening_admin", app_label=AppConfig.name)
