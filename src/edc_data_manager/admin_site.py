from edc_model_admin.admin_site import EdcAdminSite

from .apps import AppConfig

edc_data_manager_admin = EdcAdminSite(
    name="edc_data_manager_admin", app_label=AppConfig.name, keep_delete_action=True
)
