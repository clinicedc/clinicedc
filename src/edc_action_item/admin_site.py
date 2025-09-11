from edc_model_admin.admin_site import EdcAdminSite

from .apps import AppConfig

edc_action_item_admin = EdcAdminSite(name="edc_action_item_admin", app_label=AppConfig.name)
