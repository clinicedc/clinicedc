from django.apps import AppConfig as DjangoAppConfig


class AppConfig(DjangoAppConfig):
    name = "edc_crf"
    verbose_name = "Edc CRF"
    has_exportable_data = True
    include_in_administration_section = True

    def ready(self):
        from .signals import update_crf_status_post_save  # NOQA
