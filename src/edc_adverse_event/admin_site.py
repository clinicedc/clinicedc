from edc_model_admin.admin_site import EdcAdminSite

from .apps import AppConfig

edc_adverse_event_admin = EdcAdminSite(
    name="edc_adverse_event_admin", app_label=AppConfig.name
)
