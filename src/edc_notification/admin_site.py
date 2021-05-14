from edc_model_admin.admin_site import EdcAdminSite

from .apps import AppConfig

edc_notification_admin = EdcAdminSite(name="edc_notification_admin", app_label=AppConfig.name)
