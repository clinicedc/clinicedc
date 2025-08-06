from django.apps import AppConfig as DjangoAppConfig


class AppConfig(DjangoAppConfig):
    name = "edc_lab_dashboard"
    verbose_name = "Edc Lab Dashboard"
    include_in_administration_section = False
    admin_site_name = "edc_lab_admin"
