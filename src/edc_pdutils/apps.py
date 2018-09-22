import os

from django.apps import AppConfig as DjangoApponfig
from django.conf import settings


class AppConfig(DjangoApponfig):
    name = 'edc_pdutils'
    verbose_name = 'Edc Pandas Utilities'
    export_folder = os.path.join(settings.MEDIA_ROOT, 'edc_pdutils', 'export')
    include_in_administration_section = False

    def ready(self):
        os.makedirs(self.export_folder, exist_ok=True)
