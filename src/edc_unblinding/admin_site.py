from edc_model_admin.admin_site import EdcAdminSite

from .apps import AppConfig

edc_unblinding_admin = EdcAdminSite(name="edc_unblinding_admin", app_label=AppConfig.name)
