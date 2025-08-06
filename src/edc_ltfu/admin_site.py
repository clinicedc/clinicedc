from edc_model_admin.admin_site import EdcAdminSite

from .apps import AppConfig

edc_ltfu_admin = EdcAdminSite(name="edc_ltfu_admin", app_label=AppConfig.name)
