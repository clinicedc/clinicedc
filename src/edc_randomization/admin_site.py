from edc_model_admin.admin_site import EdcAdminSite

from .apps import AppConfig

edc_randomization_admin = EdcAdminSite(
    name="edc_randomization_admin", app_label=AppConfig.name
)
