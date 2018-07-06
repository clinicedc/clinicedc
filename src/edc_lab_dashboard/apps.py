import sys

from django.apps import AppConfig as DjangoAppConfig
from django.conf import settings


class AppConfig(DjangoAppConfig):
    name = 'edc_lab_dashboard'
    verbose_name = 'Edc Lab Dashboard'
    include_in_administration_section = False
    admin_site_name = 'edc_lab_admin'
    requisition_model = settings.LAB_DASHBOARD_REQUISITION_MODEL

    def ready(self):
        sys.stdout.write(f'Loading {self.verbose_name} ...\n')
        sys.stdout.write(
            f' * using requisition model \'{self.requisition_model}\'\n')
        sys.stdout.write(f' Done loading {self.verbose_name}.\n')
