from django.apps import AppConfig as DjangoAppConfig


class AppConfig(DjangoAppConfig):
    name = "edc_protocol_incident"
    verbose_name = "Edc Protocol Incidents"
    has_exportable_data = True
    include_in_administration_section = True
