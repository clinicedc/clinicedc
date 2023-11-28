from __future__ import annotations

from django.db.models import QuerySet

from ..models import ValidationErrors
from .form_validation_runner import FormValidationRunner
from .utils import get_modelform_cls


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
            modelform_cls=get_modelform_cls(self.label_lower),
            extra_formfields=extra_formfields,
            ignore_formfields=ignore_formfields,
            verbose=verbose,
        )

    def delete_validation_errors(self) -> None:
        self.validation_error_obj.delete()

    @property
    def queryset(self) -> QuerySet:
        return self.model_cls.objects.filter(id=self.validation_error_obj.src_id)
