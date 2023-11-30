from __future__ import annotations

from functools import cache
from typing import TYPE_CHECKING, Type

from django.apps import apps as django_apps
from django.contrib import admin

if TYPE_CHECKING:
    from django.contrib.admin import ModelAdmin
    from django.db.models import QuerySet
    from django.forms import ModelForm

    from .models import Issue


def get_issue_model_cls() -> Issue:
    return django_apps.get_model("edc_form_runners.issue")


@cache
def get_modelforms_from_admin_sites() -> dict[str, Type[ModelForm]]:
    registry = {}
    for admin_site in admin.sites.all_sites:
        registry.update(**get_modelforms_from_admin_site(admin_site))
    return registry


@cache
def get_modeladmins_from_admin_sites() -> dict[str, Type[ModelAdmin]]:
    registry = {}
    for admin_site in admin.sites.all_sites:
        registry.update(**get_modeladmins_from_admin_site(admin_site))
    return registry


@cache
def get_modelforms_from_admin_site(admin_site) -> dict[str, Type[ModelForm]]:
    registry = {}
    for admin_class in admin_site._registry.values():
        registry.update({admin_class.model._meta.label_lower: admin_class.form})
    return registry


@cache
def get_modeladmins_from_admin_site(admin_site) -> dict[str, Type[ModelAdmin]]:
    registry = {}
    for admin_class in admin_site._registry.values():
        registry.update({admin_class.model._meta.label_lower: admin_class})
    return registry


def get_modeladmin_cls(model_name: str) -> Type[ModelAdmin]:
    return get_modeladmins_from_admin_sites().get(model_name)


def get_modelform_cls(model_name: str) -> Type[ModelForm]:
    return get_modelforms_from_admin_sites().get(model_name)


def get_form_runner_issues(
    model_name: str, related_visit, panel_name: str | None = None
) -> QuerySet[Issue] | None:
    return get_issue_model_cls().objects.filter(
        subject_identifier=related_visit.subject_identifier,
        label_lower=model_name,
        visit_code=related_visit.visit_code,
        visit_code_sequence=related_visit.visit_code_sequence,
        visit_schedule_name=related_visit.visit_schedule_name,
        schedule_name=related_visit.schedule_name,
        panel_name=panel_name,
    )
