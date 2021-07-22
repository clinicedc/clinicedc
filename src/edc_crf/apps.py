from django.apps import AppConfig as DjangoAppConfig


class AppConfig(DjangoAppConfig):
    name = "edc_crf"
    verbose_name = "Edc CRF"
    has_exportable_data = True
    include_in_administration_section = True
