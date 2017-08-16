import os

from django.apps import AppConfig as DjangoApponfig
from django.conf import settings


class AppConfig(DjangoApponfig):
    name = 'edc_export'
    verbose_name = 'Edc Export'
    export_folder = os.path.join(settings.MEDIA_ROOT, 'edc_export', 'export')
    upload_folder = os.path.join(settings.MEDIA_ROOT, 'edc_export', 'upload')

    def ready(self):
        from .signals import export_transaction_history_on_post_save
        from .signals import export_transaction_history_on_pre_delete
        os.makedirs(self.export_folder, exist_ok=True)
        os.makedirs(self.upload_folder, exist_ok=True)
