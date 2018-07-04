import sys

from django.apps import AppConfig as DjangoAppConfig
from django.core.management.color import color_style
from django.db.models.signals import post_migrate

from .site_labs import site_labs
from django.conf import settings

style = color_style()


def update_panels_on_post_migrate(sender, **kwargs):
    site_labs.migrated = True
    site_labs.autodiscover()
    if site_labs.loaded:
        site_labs.update_panel_model(
            panel_model_cls=sender.get_model('panel'),
            sender=sender)


class AppConfig(DjangoAppConfig):
    name = 'edc_lab'
    verbose_name = 'Edc Lab'

    lab_name = 'Botswana-Harvard HIV Reference Laboratory'
    lab_address = 'Private Bag BO 320, Gaborone, Botswana'
    lab_tel = '+267 3902671 ext 2003'
    lab_fax = '+267 3901284'
    aliquot_model = 'edc_lab.aliquot'
    box_item_model = 'edc_lab.boxitem'
    box_model = 'edc_lab.box'
    manifest_item_model = 'edc_lab.manifestitem'
    manifest_model = 'edc_lab.manifest'
    result_model = 'edc_lab.result'

    def ready(self):
        from .models.signals import manifest_item_on_post_delete
        post_migrate.connect(update_panels_on_post_migrate, sender=self)
        sys.stdout.write(f'Loading {self.verbose_name} ...\n')
        site_labs.autodiscover()
        sys.stdout.write(f' Done loading {self.verbose_name}.\n')


# if settings.APP_NAME == 'edc_lab':
#
#     from dateutil.relativedelta import SU, MO, TU, WE, TH, FR, SA
#     from edc_facility.apps import AppConfig as BaseEdcFacilityAppConfig
#
#     class EdcFacilityAppConfig(BaseEdcFacilityAppConfig):
#         definitions = {
#             '7-day-clinic': dict(days=[MO, TU, WE, TH, FR, SA, SU],
#                                  slots=[100, 100, 100, 100, 100, 100, 100]),
#             '5-day-clinic': dict(days=[MO, TU, WE, TH, FR],
#                                  slots=[100, 100, 100, 100, 100]),
#             '3-day-clinic': dict(days=[TU, WE, TH],
#                                  slots=[100, 100, 100],
#                                  best_effort_available_datetime=True)}
