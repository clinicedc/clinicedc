from edc_model_admin.admin_site import EdcAdminSite

from .apps import AppConfig

edc_refusal_admin = EdcAdminSite(name="edc_refusal_admin", app_label=AppConfig.name)
