from django.apps import AppConfig as DjangoApponfig


class AppConfig(DjangoApponfig):
    name = 'edc_export'
    verbose_name = 'Edc Export'

    def ready(self):
        from .signals import export_to_transaction_on_post_save, export_to_transaction_on_pre_delete
