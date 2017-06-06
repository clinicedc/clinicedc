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
    admin_site_name = 'edc_lab_admin'

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

    aliquot_listboard_template_name = 'edc_lab/aliquot_listboard.html'
    manage_box_listboard_template_name = 'edc_lab/manage_box_listboard.html'
    requisition_listboard_template_name = 'edc_lab/requisition_listboard.html'
    receive_listboard_template_name = 'edc_lab/receive_listboard.html'
    process_listboard_template_name = 'edc_lab/process_listboard.html'
    pack_listboard_template_name = 'edc_lab/pack_listboard.html'
    manifest_listboard_template_name = 'edc_lab/manifest_listboard.html'
    manage_manifest_listboard_template_name = 'edc_lab/manage_manifest_listboard.html'
    result_listboard_template_name = 'edc_lab/result_listboard.html'
    verify_box_listboard_template_name = 'edc_lab/verify_box_listboard.html'

    home_url_name = '{}:home_url'.format(app_name)
    requisition_listboard_url_name = '{}:requisition_listboard_url'.format(
        app_name)
    receive_listboard_url_name = '{}:receive_listboard_url'.format(app_name)
    process_listboard_url_name = '{}:process_listboard_url'.format(app_name)
    pack_listboard_url_name = '{}:pack_listboard_url'.format(app_name)
    manage_box_listboard_url_name = '{}:manage_box_listboard_url'.format(
        app_name)
    aliquot_listboard_url_name = '{}:aliquot_listboard_url'.format(app_name)
    manifest_listboard_url_name = '{}:manifest_listboard_url'.format(app_name)
    manage_manifest_listboard_url_name = '{}:manage_manifest_listboard_url'.format(
        app_name)
    result_listboard_url_name = '{}:result_listboard_url'.format(app_name)
    verify_box_listboard_url_name = '{}:verify_box_listboard_url'.format(
        app_name)

    def ready(self):
        from .models.signals import manifest_item_on_post_delete
        sys.stdout.write(f'Loading {self.verbose_name} ...\n')
        site_labs.autodiscover()
        if not self.site_code:
            sys.stdout.write(style.NOTICE(f' * site code not defined. See AppConfig.\n'))
        if not self.site_name:
            sys.stdout.write(style.NOTICE(f' * site name not defined. See AppConfig.\n'))
        sys.stdout.write(f' Done loading {self.verbose_name}.\n')
