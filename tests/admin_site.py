from edc_model_admin.admin_site import EdcAdminSite

from .apps import AppConfig

test_app_admin = EdcAdminSite(name="test_app_admin", app_label=AppConfig.name)
