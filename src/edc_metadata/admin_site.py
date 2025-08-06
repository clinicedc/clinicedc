from edc_model_admin.admin_site import EdcAdminSite

from .apps import AppConfig

edc_metadata_admin = EdcAdminSite(name="edc_metadata_admin", app_label=AppConfig.name)
