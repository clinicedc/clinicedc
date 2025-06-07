from django.apps import AppConfig as BaseAppConfig


class AppConfig(BaseAppConfig):
    name = "edc_reportable"
    verbose_name = "Edc Reportable"
    app_label = "edc_reportable"
    has_exportable_data = True
    include_in_administration_section = True
