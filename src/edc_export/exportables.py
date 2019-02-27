from collections import OrderedDict
from django.apps import apps as django_apps
from django.contrib import messages
from django.contrib.admin import sites
from django.core.exceptions import ObjectDoesNotExist
from edc_permissions.constants.group_names import EXPORT

from .model_options import ModelOptions


class Exportables(OrderedDict):

    """A dictionary-like object that creates a "list" of
    models that may be exported.

    Checks each AppConfig.has_exportable_data and if True
    includes that apps models, including historical and list models.
    """

    export_group_name = EXPORT

    def __init__(self, app_configs=None, user=None, request=None):
        super().__init__()
        self._inlines = {}
        app_configs = app_configs or self.get_app_configs()
        app_configs.sort(key=lambda x: x.verbose_name)

        try:
            user.groups.get(name=self.export_group_name)
        except ObjectDoesNotExist:
            messages.error(
                request, "You do not have sufficient permissions to export data."
            )
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
                    "models": models,
                    "inlines": self.inlines.get(model._meta.app_label),
                    "historicals": historical_models,
                    "lists": list_models,
                }
                self.update({app_config: exportable})

    @property
    def inlines(self):
        if not self._inlines:
            for site in sites.all_sites:
                for model_cls, admin_site in site._registry.items():
                    for inline_cls in admin_site.inlines:
                        model_opts = ModelOptions(
                            model=inline_cls.model._meta.label_lower
                        )
                        try:
                            self._inlines[model_cls._meta.app_label].append(model_opts)
                        except KeyError:
                            self._inlines[model_cls._meta.app_label] = [model_opts]
                        self._inlines[model_cls._meta.app_label].sort(
                            key=lambda x: x.verbose_name.title()
                        )
        return self._inlines

    def get_app_configs(self):
        """Returns a list of app_configs with exportable data.
        """
        app_configs = []
        for app_config in django_apps.get_app_configs():
            try:
                has_exportable_data = app_config.has_exportable_data
            except AttributeError:
                has_exportable_data = None
            if has_exportable_data:
                app_configs.append(app_config)
        return app_configs
