import sys

from django.apps import AppConfig as DjangoAppConfig

from .site_labs import site_labs
from .lab import Manifest

app_name = 'edc_lab'


class AppConfig(DjangoAppConfig):
    name = 'edc_lab'
    verbose_name = 'Edc Lab'
    admin_site_name = 'edc_lab_admin'

    aliquot_model = 'edc_lab.aliquot'
    box_model = 'edc_lab.box'
    box_item_model = 'edc_lab.boxitem'
    requisition_model = None
    result_model = None
    manifest_model = 'edc_lab.manifest'
    box_model = 'edc_lab.box'

    manifest = Manifest(
        destinations={'bhhrl': 'BHHRL'},
        default_destination='bhhrl')

    aliquot_listboard_template_name = 'edc_lab/aliquot_listboard.html'
    box_listboard_template_name = 'edc_lab/box_listboard.html'
    requisition_listboard_template_name = 'edc_lab/requisition_listboard.html'
    receive_listboard_template_name = 'edc_lab/receive_listboard.html'
    pack_listboard_template_name = 'edc_lab/pack_listboard.html'
    manifest_listboard_template_name = 'edc_lab/manifest_listboard.html'
    result_listboard_template_name = 'edc_lab/result_listboard.html'

    home_url_name = '{}:home_url'.format(app_name)
    requisition_listboard_url_name = '{}:requisition_listboard_url'.format(
        app_name)
    receive_listboard_url_name = '{}:receive_listboard_url'.format(app_name)
    process_listboard_url_name = '{}:process_listboard_url'.format(app_name)
    pack_listboard_url_name = '{}:pack_listboard_url'.format(app_name)
    box_listboard_url_name = '{}:box_listboard_url'.format(app_name)
    aliquot_listboard_url_name = '{}:aliquot_listboard_url'.format(app_name)
    manifest_listboard_url_name = '{}:manifest_listboard_url'.format(app_name)
    result_listboard_url_name = '{}:result_listboard_url'.format(app_name)

    def ready(self):
        from .models.signals import box_item_on_post_save
        sys.stdout.write('Loading {} ...\n'.format(self.verbose_name))
        site_labs.autodiscover()
        sys.stdout.write(' Done loading {}.\n'.format(self.verbose_name))
