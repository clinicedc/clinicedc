import os

from django.apps import AppConfig as DjangoApponfig
from django.conf import settings


class AppConfig(DjangoApponfig):
    name = 'edc_pdutils'
    verbose_name = 'Edc Export'
    export_folder = os.path.join(settings.MEDIA_ROOT, 'edc_pdutils', 'export')

    def ready(self):
        os.makedirs(self.export_folder, exist_ok=True)
