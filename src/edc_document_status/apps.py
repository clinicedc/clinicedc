from django.apps import AppConfig as DjangoAppConfig


class AppConfig(DjangoAppConfig):
    name = "edc_document_status"
    verbose_name = "Edc Document Status"
    has_exportable_data = False
    include_in_administration_section = False
