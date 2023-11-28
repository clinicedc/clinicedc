from __future__ import annotations

from typing import Type

from django.apps import apps as django_apps
from django.contrib import admin
from django.core.exceptions import FieldError
from django.forms import ModelForm

from .exceptions import FormValidationRunnerError
from .form_validation_runner import FormValidationRunner


def get_modelform_cls(label_lower) -> Type[ModelForm]:
    model_cls = django_apps.get_model(label_lower)
    for s in admin.sites.all_sites:
        if s.name.startswith(model_cls._meta.app_label):
            if s._registry.get(model_cls):
                return s._registry.get(model_cls).form
            break
    raise FormValidationRunnerError(f"Unable to determine modelform_cls. Got {label_lower}")


def rerun_form_validation(
    app_labels: list[str] | None = None, model_names: list[str] | None = None
):
    models = []
    if app_labels:
        for app_config in django_apps.get_app_configs():
            if app_config.name in app_labels:
                models = [model_cls for model_cls in app_config.get_models()]
    if model_names:
        for model_name in model_names:
            models.append(django_apps.get_model(model_name))
    for model_cls in models:
        print(model_cls._meta.label_lower)
        try:
            modelform = get_modelform_cls(model_cls._meta.label_lower)
        except FormValidationRunnerError as e:
            print(e)
        else:
            print(modelform)
            try:
                FormValidationRunner(modelform).run()
            except (AttributeError, FieldError) as e:
                print(f"{e}. See {model_cls._meta.label_lower}.")
