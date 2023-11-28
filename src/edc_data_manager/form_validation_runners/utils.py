from __future__ import annotations

from typing import Type

from django.apps import apps as django_apps
from django.contrib import admin
from django.forms import ModelForm

from .exceptions import FormValidationRunnerError


def get_modelform_cls(label_lower) -> Type[ModelForm]:
    model_cls = django_apps.get_model(label_lower)
    for s in admin.sites.all_sites:
        if s.name.startswith(model_cls._meta.app_label):
            if s._registry.get(model_cls):
                return s._registry.get(model_cls).form
            break
    raise FormValidationRunnerError(f"Unable to determine modelform_cls. Got {label_lower}")
