from edc_model_admin.admin_site import EdcAdminSite

from .apps import AppConfig

edc_label_admin = EdcAdminSite(name="edc_label_admin", app_label=AppConfig.name)
