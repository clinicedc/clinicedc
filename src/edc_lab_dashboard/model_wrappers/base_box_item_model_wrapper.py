from django.apps import apps as django_apps
from edc_model_wrapper import ModelWrapper

edc_lab_app_config = django_apps.get_app_config('edc_lab')


class BaseBoxItemModelWrapper(ModelWrapper):

    model = edc_lab_app_config.box_item_model
    action_name = None
    next_url_name = None
    next_url_attrs = ['box_identifier', 'action_name']

    @property
    def human_readable_identifier(self):
        return self.object.human_readable_identifier

    @property
    def box_identifier(self):
        return self.object.box.box_identifier
