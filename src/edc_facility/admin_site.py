from edc_model_admin.admin_site import EdcAdminSite

from .apps import AppConfig

edc_facility_admin = EdcAdminSite(name="edc_facility_admin", app_label=AppConfig.name)
