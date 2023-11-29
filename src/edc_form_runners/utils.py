from __future__ import annotations

from functools import cache
from typing import TYPE_CHECKING, Type

from django.apps import apps as django_apps
from django.contrib import admin
from django.core.exceptions import FieldError
from django.db.models import QuerySet
from django.forms import ModelForm

from .exceptions import FormRunnerError
from .form_runner import FormRunner

if TYPE_CHECKING:
    from .models import Issue


@cache
def get_modelforms_from_admin_site(admin_site):
    registry = {}
    for admin_class in admin_site._registry.values():
        registry.update({admin_class.model._meta.label_lower: admin_class.form})
    return registry


@cache
def get_modelforms_from_admin_sites():
    registry = {}
    for admin_site in admin.sites.all_sites:
        registry.update(**get_modelforms_from_admin_site(admin_site))
    return registry


def get_modelform_cls(label_lower: str) -> Type[ModelForm]:
    return get_modelforms_from_admin_sites().get(label_lower)


def run_form_runners(
    app_labels: list[str] | None = None, model_names: list[str] | None = None
):
    models = []
    if app_labels:
        for app_config in django_apps.get_app_configs():
            if app_config.name in app_labels:
                models = [model_cls for model_cls in app_config.get_models()]
    elif model_names:
        for model_name in model_names:
            models.append(django_apps.get_model(model_name))
    else:
        raise FormRunnerError("Nothing to do.")
    modelforms = []
    for model_cls in models:
        if modelform_cls := get_modelform_cls(model_cls._meta.label_lower):
            modelforms.append((modelform_cls, model_cls))
    for modelform_cls, model_cls in modelforms:
        print(model_cls._meta.label_lower)
        try:
            FormRunner(modelform_cls, model_cls).run()
        except (AttributeError, FieldError) as e:
            print(f"{e}. See {model_cls._meta.label_lower}.")


def get_form_runner_issues(
    label_lower: str, related_visit, panel_name: str | None = None
) -> QuerySet[Issue] | None:
    issues_model_cls = django_apps.get_model("edc_form_runners.issue")
    return issues_model_cls.objects.filter(
        subject_identifier=related_visit.subject_identifier,
        label_lower=label_lower,
        visit_code=related_visit.visit_code,
        visit_code_sequence=related_visit.visit_code_sequence,
        visit_schedule_name=related_visit.visit_schedule_name,
        schedule_name=related_visit.schedule_name,
        panel_name=panel_name,
    )
