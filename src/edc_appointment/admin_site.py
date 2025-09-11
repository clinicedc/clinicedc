from edc_model_admin.admin_site import EdcAdminSite

from .apps import AppConfig

edc_appointment_admin = EdcAdminSite(name="edc_appointment_admin", app_label=AppConfig.name)
