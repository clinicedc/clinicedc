from __future__ import annotations

from typing import Type

from django.apps import apps as django_apps
from django.contrib import admin
from django.db.models import QuerySet
from django.forms import ModelForm

from ..models import ValidationErrors
from .exceptions import FormValidationRunnerError
from .form_validation_runner import FormValidationRunner


class SingleFormValidationRunner(FormValidationRunner):
    def __init__(
        self,
        validation_error_obj: ValidationErrors,
        verbose: bool | None = None,
    ):
        extra_formfields = None
        ignore_formfields = None
        self.validation_error_obj = validation_error_obj
        self.label_lower = self.validation_error_obj.label_lower
        if self.validation_error_obj.extra_formfields:
            extra_formfields = self.validation_error_obj.extra_formfields.split(",")
        if self.validation_error_obj.ignore_formfields:
            ignore_formfields = self.validation_error_obj.ignore_formfields.split(",")

        super().__init__(
            modelform_cls=self.get_modelform_cls(),
            extra_formfields=extra_formfields,
            ignore_formfields=ignore_formfields,
            verbose=verbose,
        )

    def delete_validation_errors(self) -> None:
        self.validation_error_obj.delete()

    @property
    def queryset(self) -> QuerySet:
        return self.model_cls.objects.filter(id=self.validation_error_obj.src_id)

    def get_modelform_cls(self) -> Type[ModelForm]:
        model_cls = django_apps.get_model(self.label_lower)
        for s in admin.sites.all_sites:
            if s.name.startswith(model_cls._meta.app_label):
                return s._registry.get(model_cls).form
        raise FormValidationRunnerError(
            f"Unable to determine modelform_cls. Got {self.label_lower}"
        )
