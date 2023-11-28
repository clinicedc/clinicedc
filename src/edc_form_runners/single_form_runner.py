from __future__ import annotations

from django.db.models import QuerySet

from .form_runner import FormRunner
from .models import Issue
from .utils import get_modelform_cls


class SingleFormRunner(FormRunner):
    def __init__(
        self,
        issue_obj: Issue,
        verbose: bool | None = None,
    ):
        extra_formfields = None
        ignore_formfields = None
        self.issue_obj = issue_obj
        self.label_lower = self.issue_obj.label_lower
        if self.issue_obj.extra_formfields:
            extra_formfields = self.issue_obj.extra_formfields.split(",")
        if self.issue_obj.ignore_formfields:
            ignore_formfields = self.issue_obj.ignore_formfields.split(",")

        super().__init__(
            modelform_cls=get_modelform_cls(self.label_lower),
            extra_formfields=extra_formfields,
            ignore_formfields=ignore_formfields,
            verbose=verbose,
        )

    def delete_issues(self) -> None:
        self.issue_obj.delete()

    @property
    def queryset(self) -> QuerySet:
        return self.model_cls.objects.filter(id=self.issue_obj.src_id)
