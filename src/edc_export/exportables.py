from collections import OrderedDict
from django.apps import apps as django_apps
from django.conf import settings
from django.contrib import messages
from django.contrib.admin import sites
from django.core.exceptions import ObjectDoesNotExist
from edc_auth import EXPORT
from edc_randomization.blinding import is_blinded_user
from edc_randomization.site_randomizers import site_randomizers

from .model_options import ModelOptions


def is_randomization_list_model(model=None, user=None):
    """Returns True if user has permission to access
    randomization list models."""
    is_randomization_list_model = False
    for randomizer in site_randomizers._registry.values():
        if (
            model._meta.label_lower == randomizer.model
            or model._meta.label_lower
            == randomizer.model_cls().history.model._meta.label_lower
        ):
            if is_blinded_user(user.username):
                is_randomization_list_model = True
                break
    return is_randomization_list_model


class Exportable(OrderedDict):
    def __init__(self, app_config=None, user=None):
        super().__init__()
        self._inlines = {}
        self.app_config = app_config
        self.historical_models = []
        self.list_models = []
        self.models = []
        self.name = app_config.name
        self.verbose_name = app_config.verbose_name
        for model in app_config.get_models():
            if is_randomization_list_model(model=model, user=user):
                continue
            model_opts = ModelOptions(model=model._meta.label_lower)
            if model_opts.is_historical:
                self.historical_models.append(model_opts)
            elif model_opts.is_list_model:
                self.list_models.append(model_opts)
            else:
                if not model._meta.proxy:
                    self.models.append(model_opts)
        self.models.sort(key=lambda x: x.verbose_name.title())
        self.historical_models.sort(key=lambda x: x.verbose_name.title())
        self.list_models.sort(key=lambda x: x.verbose_name.title())
        self.inlines = self.get_inlines(app_config.name)
        self.update(
            dict(
                models=self.models,
                historical_models=self.historical_models,
                list_models=self.list_models,
                inlines=self.inlines,
            )
        )

    def __repr__(self):
        return f"{self.__class__.__name__}(app_config={self.app_config})"

    def __str__(self):
        return self.name

    def get_inlines(self, app_label):
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
        return self._inlines.get(app_label)


class Exportables(OrderedDict):
    """A dictionary-like object that creates a "list" of
    models, historical models, and list models that may be exported.

    Checks each `AppConfig.has_exportable_data` and if True
    includes that apps models, including historical and list models.
    """

    export_group_name = EXPORT

    default_app_labels = getattr(
        settings, "EDC_EXPORTABLE_DEFAULT_APPS", ["sites", "auth", "admin"],
    )

    def __init__(self, app_configs=None, user=None, request=None):
        super().__init__()
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
                self.update(
                    {app_config.name: Exportable(app_config=app_config, user=user)}
                )

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
        for app_label in self.default_app_labels:
            app_configs.append(django_apps.get_app_config(app_label))
        return app_configs
