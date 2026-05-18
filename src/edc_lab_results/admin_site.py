from edc_model_admin.admin_site import EdcAdminSite

from .apps import AppConfig

edc_lab_results_admin = EdcAdminSite(
    name="edc_lab_results_admin", app_label=AppConfig.name
)
