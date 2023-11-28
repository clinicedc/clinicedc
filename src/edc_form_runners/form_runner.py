from __future__ import annotations

import html
import uuid
from typing import TYPE_CHECKING, Any, Type

from bs4 import BeautifulSoup
from django.db.models import ForeignKey, ManyToManyField, OneToOneField, QuerySet
from edc_utils import get_utcnow
from tqdm import tqdm

from .models import Issue

if TYPE_CHECKING:
    from django.forms import ModelForm


class FormRunner:
    """Rerun modelform validation on all instances of a model.

    Usage:
        runner = FormRunner(MyModelform)
        runner.run()
    """

    def __init__(
        self,
        modelform_cls: Type[ModelForm] | None = None,
        extra_formfields: list[str] | None = None,
        ignore_formfields: list[str] | None = None,
        verbose: bool | None = None,
        filter_options: dict[str, str] | None = None,
    ):
        self.session_id = uuid.uuid4()
        self.session_datetime = get_utcnow()
        self.verbose = True if verbose is None else verbose
        self.modelform_cls = modelform_cls
        self.model_cls = modelform_cls._meta.model
        self.extra_formfields = extra_formfields or []
        self.ignore_formfields = ignore_formfields or []
        self.filter_options = filter_options

    def run(self):
        self.delete_issues()
        total = self.queryset.count()
        for model_obj in tqdm(self.queryset.order_by("created"), total=total):
            data = self.get_form_data(model_obj)
            form = self.modelform_cls(data, instance=model_obj)
            form.is_valid()
            errors = {k: v for k, v in form._errors.items() if k not in self.ignore_formfields}
            if errors:
                for k, v in errors.items():
                    issue_obj = self.write_to_db(k, v, model_obj)
                    if self.verbose:
                        print(issue_obj)

    def delete_issues(self) -> None:
        Issue.objects.filter(label_lower=self.model_cls._meta.label_lower).delete()

    @property
    def queryset(self) -> QuerySet:
        opts = {}
        if self.filter_options:
            opts = dict(**self.filter_options)
        return self.model_cls.objects.filter(**opts)

    def get_form_data(self, model_obj) -> dict:
        data = {
            k: v
            for k, v in model_obj.__dict__.items()
            if not k.startswith("_") and not k.endswith("_id")
        }
        for fld_cls in model_obj._meta.get_fields():
            if isinstance(fld_cls, (ForeignKey, OneToOneField)):
                try:
                    obj_fld_id = getattr(model_obj, fld_cls.name).id
                except AttributeError:
                    rel_obj = None
                else:
                    rel_obj = fld_cls.related_model.objects.get(id=obj_fld_id)
                data.update({fld_cls.name: rel_obj})
            elif isinstance(fld_cls, (ManyToManyField,)):
                data.update({fld_cls.name: getattr(model_obj, fld_cls.name).all()})
            else:
                pass
        try:
            data.update(subject_visit=model_obj.subject_visit)
        except AttributeError:
            data.update(subject_identifier=model_obj.subject_identifier)
        for extra_formfield in self.extra_formfields:
            data.update({extra_formfield: getattr(model_obj, extra_formfield)})
        return data

    def write_to_db(self, k: str, v: Any, model_obj) -> Issue:
        model_obj_or_related_visit = getattr(model_obj, "subject_visit", model_obj)
        subject_identifier = model_obj_or_related_visit.subject_identifier
        visit_code = model_obj_or_related_visit.visit_code
        visit_code_sequence = model_obj_or_related_visit.visit_code_sequence
        raw_message = html.unescape(v.as_text())
        message = BeautifulSoup(raw_message, "html.parser").text
        try:
            response = getattr(model_obj, k)
        except AttributeError:
            response = None
        return Issue.objects.create(
            session_id=self.session_id,
            session_datetime=self.session_datetime,
            label_lower=model_obj._meta.label_lower,
            verbose_name=model_obj._meta.verbose_name,
            subject_identifier=subject_identifier,
            visit_code=visit_code,
            visit_code_sequence=visit_code_sequence,
            field_name=k,
            raw_message=raw_message,
            message=message,
            short_message=message[:250],
            response=str(response),
            src_id=model_obj.id,
            src_revision=model_obj.revision,
            src_report_datetime=getattr(model_obj, "report_datetime", None),
            src_modified_datetime=model_obj.modified,
            src_user_modified=model_obj.user_modified,
            site=model_obj.site,
            extra_formfields=",".join(self.extra_formfields),
            ignore_formfields=",".join(self.ignore_formfields),
        )
