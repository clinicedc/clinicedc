from edc_model_admin.admin_site import EdcAdminSite

from .apps import AppConfig

edc_pdutils_admin = EdcAdminSite(name="edc_pdutils_admin", app_label=AppConfig.name)
