from edc_model_admin.admin_site import EdcAdminSite

from .apps import AppConfig

edc_identifier_admin = EdcAdminSite(name="edc_identifier_admin", app_label=AppConfig.name)
