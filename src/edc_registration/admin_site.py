from edc_model_admin.admin_site import EdcAdminSite

from .apps import AppConfig

edc_registration_admin = EdcAdminSite(name="edc_registration_admin", app_label=AppConfig.name)
