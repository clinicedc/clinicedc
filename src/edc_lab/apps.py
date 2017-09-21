import sys

from django.apps import AppConfig as DjangoAppConfig
from django.conf import settings
from django.core.management.color import color_style

from .site_labs import site_labs

app_name = 'edc_lab'

style = color_style()


class AppConfig(DjangoAppConfig):
    name = 'edc_lab'
    verbose_name = 'Edc Lab'

    lab_name = 'Botswana-Harvard HIV Reference Laboratory'
    lab_address = 'Private Bag BO 320, Gaborone, Botswana'
    lab_tel = '+267 3902671 ext 2003'
    lab_fax = '+267 3901284'

    site_code = None
    site_name = None

    aliquot_model = 'edc_lab.aliquot'

    box_model = 'edc_lab.box'
    box_item_model = 'edc_lab.boxitem'
    try:
        requisition_model = settings.EDC_LAB_REQUISITION_MODEL
    except AttributeError:
        requisition_model = None
    result_model = None
    manifest_model = 'edc_lab.manifest'
    manifest_item_model = 'edc_lab.manifestitem'
    box_model = 'edc_lab.box'

    def ready(self):
        from .models.signals import manifest_item_on_post_delete
        sys.stdout.write(f'Loading {self.verbose_name} ...\n')
        site_labs.autodiscover()
        if not self.site_code:
            sys.stdout.write(style.NOTICE(
                f' * site code not defined. See AppConfig.\n'))
        if not self.site_name:
            sys.stdout.write(style.NOTICE(
                f' * site name not defined. See AppConfig.\n'))
        sys.stdout.write(f' Done loading {self.verbose_name}.\n')
