from django.apps import AppConfig as DjangoAppConfig


class AppConfig(DjangoAppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "edc_pylabels"
    verbose_name = "Edc Labels"
    include_in_administration_section = True
