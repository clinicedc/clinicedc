from edc_model_admin.admin_site import EdcAdminSite

from .apps import AppConfig

edc_rx_admin = EdcAdminSite(name="edc_rx_admin", app_label=AppConfig.name)
