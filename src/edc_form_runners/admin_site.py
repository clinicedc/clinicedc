from edc_model_admin.admin_site import EdcAdminSite

from .apps import AppConfig

__all__ = ["edc_form_runners_admin"]

edc_form_runners_admin = EdcAdminSite(
    name="edc_form_runners_admin", app_label=AppConfig.name, keep_delete_action=True
)
