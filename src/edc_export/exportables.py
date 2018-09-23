from collections import OrderedDict
from django.apps import apps as django_apps
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from edc_permissions.constants.group_names import EXPORT

from .model_options import ModelOptions


class Exportables(OrderedDict):

    """A dictionary-like object that creates a "list" of
    models that may be exported.

    Checks each AppConfig.has_exportable_data and if True
    includes that apps models, including historical and list models.
    """

    def __init__(self, app_configs=None, user=None, request=None):
        super().__init__()
        app_configs = app_configs or self.get_app_configs()
        app_configs.sort(key=lambda x: x.verbose_name)
        try:
            user.groups.get(name=EXPORT)
        except ObjectDoesNotExist:
            messages.error(
                request, 'You do not have sufficient permissions to export data.')
        else:
            for app_config in app_configs:
                models = []
                historical_models = []
                list_models = []
                for model in app_config.get_models():
                    model_opts = ModelOptions(model=model._meta.label_lower)
                    if model_opts.is_historical:
                        historical_models.append(model_opts)
                    elif model_opts.is_list_model:
                        list_models.append(model_opts)
                    else:
                        models.append(model_opts)
                models.sort(key=lambda x: x.verbose_name.title())
                historical_models.sort(key=lambda x: x.verbose_name.title())
                list_models.sort(key=lambda x: x.verbose_name.title())
                exportable = {
                    'models': models,
                    'historicals': historical_models,
                    'lists': list_models}
                self.update({app_config: exportable})

    def get_app_configs(self):
        app_configs = []
        for app_config in django_apps.get_app_configs():
            try:
                has_exportable_data = app_config.has_exportable_data
            except AttributeError:
                has_exportable_data = None
            if has_exportable_data:
                app_configs.append(app_config)
        return app_configs
