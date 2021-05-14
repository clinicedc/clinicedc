from edc_model_admin.admin_site import EdcAdminSite

from .apps import AppConfig

edc_visit_tracking_admin = EdcAdminSite(
    name="edc_visit_tracking_admin", app_label=AppConfig.name
)
