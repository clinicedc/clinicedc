from edc_model_admin.admin_site import EdcAdminSite

from .apps import AppConfig

edc_crf_admin = EdcAdminSite(name="edc_crf_admin", app_label=AppConfig.name)
