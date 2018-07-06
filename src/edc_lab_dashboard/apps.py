from django.apps import AppConfig as DjangoAppConfig
from django.conf import settings


class AppConfig(DjangoAppConfig):
    name = 'edc_lab_dashboard'
    include_in_administration_section = False
    admin_site_name = 'edc_lab_admin'
    requisition_model = settings.LAB_DASHBOARD_REQUISITION_MODEL
