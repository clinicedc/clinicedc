import sys

from django.apps import AppConfig as DjangoAppConfig

from .site_labs import site_labs
from .manifest import Manifest


class AppConfig(DjangoAppConfig):
    name = 'edc_lab'
    verbose_name = 'Edc Lab'
    admin_site_name = 'edc_lab_admin'

    aliquot_model = 'edc_lab.aliquot'
    requisition_model = None
    result_model = None
    manifest_model = 'edc_lab.manifest'

    manifest = Manifest(
        destinations={'bhhrl': 'BHHRL'},
        default_destination='bhhrl')

    aliquot_listboard_template_name = 'edc_lab/aliquot_listboard.html'
    requisition_listboard_template_name = 'edc_lab/requisition_listboard.html'
    result_listboard_template_name = 'edc_lab/result_listboard.html'
    manifest_listboard_template_name = 'edc_lab/manifest_listboard.html'

    home_url_name = 'edc-lab:home_url'
    requisition_listboard_url_name = 'edc-lab:requisition_listboard_url'
    receive_listboard_url_name = 'edc-lab:receive_listboard_url'
    process_listboard_url_name = 'edc-lab:process_listboard_url'
    pack_listboard_url_name = 'edc-lab:pack_listboard_url'
    aliquot_listboard_url_name = 'edc-lab:aliquot_listboard_url'
    manifest_listboard_url_name = 'edc-lab:manifest_listboard_url'
    result_listboard_url_name = 'edc-lab:result_listboard_url'

    def ready(self):
        sys.stdout.write('Loading {} ...\n'.format(self.verbose_name))
        site_labs.autodiscover()
        sys.stdout.write(' Done loading {}.\n'.format(self.verbose_name))
