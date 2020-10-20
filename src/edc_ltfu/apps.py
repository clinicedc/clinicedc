from django.apps import AppConfig as DjangoAppConfig


class AppConfig(DjangoAppConfig):
    name = "edc_ltfu"
    verbose_name = "Edc Loss to Follow up"
    has_exportable_data = False
    include_in_administration_section = False
