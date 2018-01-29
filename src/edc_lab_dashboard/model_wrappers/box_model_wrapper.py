from django.apps import apps as django_apps
from edc_model_wrapper import ModelWrapper
from ..dashboard_urls import dashboard_urls

edc_lab_app_config = django_apps.get_app_config('edc_lab')


class BoxModelWrapper(ModelWrapper):

    model = edc_lab_app_config.box_model
    next_url_name = dashboard_urls.get('pack_listboard_url')

    @property
    def human_readable_identifier(self):
        return self.object.human_readable_identifier
