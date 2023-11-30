from __future__ import annotations

import html
import uuid
from typing import TYPE_CHECKING, Any

from bs4 import BeautifulSoup
from django.apps import apps as django_apps
from django.db.models import ForeignKey, ManyToManyField, Model, OneToOneField, QuerySet
from edc_utils import get_utcnow
from tqdm import tqdm

from .exceptions import FormRunnerModelAdminNotFound
from .utils import get_modeladmin_cls

if TYPE_CHECKING:
    from .models import Issue


class FormRunner:
    """Rerun modelform validation on all instances of a model"""

    model_name: str | None = None
    issue_model = "edc_form_runners.issue"
    extra_formfields: list[str] | None = None
    exclude_formfields: list[str] | None = None

    def __init__(
        self,
        model_name: str | None = None,
        src_filter_options: dict[str, Any] | None = None,
        verbose: bool | None = None,
    ) -> None:
        self.session_id = uuid.uuid4()
        self.session_datetime = get_utcnow()
        self.verbose = verbose
        self.model_name = self.model_name or model_name
        self.modeladmin_cls = get_modeladmin_cls(self.model_name)
        if not self.modeladmin_cls:
            raise FormRunnerModelAdminNotFound(
                "No modeladmin or modelform class found. Is this model registered with Admin? "
                f"Got `{model_name}`."
            )
        self.src_model_cls = self.modeladmin_cls.model
        self.modelform_cls = self.modeladmin_cls.form
        self.src_filter_options = src_filter_options

    def __repr__(self):
        return f"{self.__class__}({self.model_name})"

    def __str__(self):
        return self.model_name

    def run_all(self) -> None:
        total = self.src_qs.count()
        for src_obj in tqdm(self.src_qs, total=total):
            self.issue_model_cls.objects.filter(**self.unique_opts(src_obj)).delete()
            self.run_one(src_obj=src_obj, skip_delete=True)

    def run_one(self, src_obj: Model, skip_delete: bool | None = None) -> None:
        if not skip_delete:
            self.issue_model_cls.objects.filter(**self.unique_opts(src_obj)).delete()
        data = self.get_form_data(src_obj)
        form = self.modelform_cls(data, instance=src_obj)
        form.is_valid()
        errors = {
            k: v for k, v in form._errors.items() if k not in self.get_exclude_formfields()
        }
        if errors:
            for fldname, errmsg in errors.items():
                issue_obj = self.write_to_db(fldname, errmsg, src_obj)
                self.print(str(issue_obj))

    @property
    def issue_model_cls(self) -> Issue:
        return django_apps.get_model(self.issue_model)

    def write_to_db(self, fldname: str, errmsg: Any, src_obj: Any) -> Issue:
        raw_message = html.unescape(errmsg.as_text())
        message = BeautifulSoup(raw_message, "html.parser").text
        try:
            response = getattr(src_obj, fldname)
        except AttributeError:
            response = None
        return self.issue_model_cls.objects.create(
            session_id=self.session_id,
            session_datetime=self.session_datetime,
            raw_message=raw_message,
            message=message,
            short_message=message[:250],
            response=str(response),
            src_id=src_obj.id,
            src_revision=src_obj.revision,
            src_report_datetime=getattr(src_obj, "report_datetime", None),
            src_modified_datetime=src_obj.modified,
            src_user_modified=src_obj.user_modified,
            field_name=fldname,
            site=src_obj.site,
            extra_formfields=",".join(self.get_extra_formfields()),
            exclude_formfields=",".join(self.get_exclude_formfields()),
            **self.unique_opts(src_obj),
        )

    def unique_opts(self, src_obj) -> dict[str, Any]:
        model_obj_or_related_visit = getattr(src_obj, "subject_visit", src_obj)
        subject_identifier = model_obj_or_related_visit.subject_identifier
        visit_code = model_obj_or_related_visit.visit_code
        visit_code_sequence = model_obj_or_related_visit.visit_code_sequence
        visit_schedule_name = model_obj_or_related_visit.visit_schedule_name
        schedule_name = model_obj_or_related_visit.schedule_name
        return dict(
            label_lower=src_obj._meta.label_lower,
            panel_name=self.get_panel_name(src_obj),
            verbose_name=src_obj._meta.verbose_name,
            subject_identifier=subject_identifier,
            visit_code=visit_code,
            visit_code_sequence=visit_code_sequence,
            visit_schedule_name=visit_schedule_name,
            schedule_name=schedule_name,
        )

    @staticmethod
    def get_panel_name(src_obj) -> str | None:
        panel = getattr(src_obj, "panel", None)
        return getattr(panel, "name", None)

    @property
    def src_qs(self) -> QuerySet:
        return self.src_model_cls.objects.filter(**(self.get_src_filter_options() or {}))

    def get_form_data(self, src_obj: Any) -> dict[str, Any]:
        data = {
            k: v
            for k, v in src_obj.__dict__.items()
            if not k.startswith("_") and not k.endswith("_id")
        }
        for fld_cls in src_obj._meta.get_fields():
            if isinstance(fld_cls, (ForeignKey, OneToOneField)):
                try:
                    obj_fld_id = getattr(src_obj, fld_cls.name).id
                except AttributeError:
                    rel_obj = None
                else:
                    rel_obj = fld_cls.related_model.objects.get(id=obj_fld_id)
                data.update({fld_cls.name: rel_obj})
            elif isinstance(fld_cls, (ManyToManyField,)):
                data.update({fld_cls.name: getattr(src_obj, fld_cls.name).all()})
            else:
                pass
        try:
            data.update(subject_visit=src_obj.subject_visit)
        except AttributeError:
            data.update(subject_identifier=src_obj.subject_identifier)
        for extra_formfield in self.get_extra_formfields():
            data.update({extra_formfield: getattr(src_obj, extra_formfield)})
        return data

    def get_src_filter_options(self) -> dict[str, Any]:
        return self.src_filter_options

    def get_extra_formfields(self) -> list[str]:
        return self.extra_formfields or []

    def get_exclude_formfields(self) -> list[str]:
        return self.exclude_formfields or []

    def print(self, msg: str) -> None:
        if self.verbose:
            print(msg)
