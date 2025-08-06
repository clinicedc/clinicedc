from edc_model_admin.admin_site import EdcAdminSite

from .apps import AppConfig

edc_reportable_admin = EdcAdminSite(name="edc_reportable_admin", app_label=AppConfig.name)
