from django.apps import AppConfig as DjangoAppConfig


class AppConfig(DjangoAppConfig):
    name = 'edc_dashboard'

    listboard_template_name = None
    include_in_administration_section = False
