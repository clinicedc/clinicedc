from edc_model_admin.admin_site import EdcAdminSite as BaseEdcAdminSite

from .apps import AppConfig


class EdcAdminSite(BaseEdcAdminSite):
    index_template = "edc_adverse_event/admin/index.html"
    app_index_template = "edc_adverse_event/admin/app_index.html"


edc_adverse_event_admin = EdcAdminSite(
    name="edc_adverse_event_admin", app_label=AppConfig.name
)
