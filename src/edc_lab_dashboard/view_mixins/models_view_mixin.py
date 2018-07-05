from django.apps import apps as django_apps
from edc_lab.models import Aliquot, Box, BoxItem


edc_lab_app_config = django_apps.get_app_config('edc_lab')


class ModelsViewMixin:

    @property
    def box_model(self):
        return Box

    @property
    def box_item_model(self):
        return BoxItem

    @property
    def manifest_model(self):
        return django_apps.get_model(edc_lab_app_config.manifest_model)

    @property
    def requisition_model(self):
        return django_apps.get_model(edc_lab_app_config.requisition_model)
