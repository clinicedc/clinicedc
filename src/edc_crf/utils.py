from django import forms
from django.apps import apps as django_apps
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.utils.text import format_lazy
from django.utils.translation import gettext_lazy as _

from edc_model import model_exists_or_raise


def raise_if_crf_does_not_exist(subject_visit, model: str) -> None:
    model_cls = django_apps.get_model(model)
    try:
        model_exists_or_raise(subject_visit=subject_visit, model_cls=model_cls)
    except ObjectDoesNotExist:
        complete = _("Complete")
        crf_first = _("CRF first")
        verbose_name = model_cls._meta.verbose_name
        err_message = format_lazy(
            "{complete} {verbose_name} {crf_first}",
            complete=complete,
            crf_first=crf_first,
            verbose_name=verbose_name,
        )
        raise forms.ValidationError(err_message)


class HasCrfChecker:
    def __init__(
        self,
        app_name: str,
        subject_visit_model_cls,
    ):
        self.app_name = app_name
        self.subject_visit_model_cls = subject_visit_model_cls
        self.models = []
        for model in django_apps.get_app_config(self.app_name).get_models():
            if model._meta.label_lower.split(".")[1].startswith("historical"):
                continue
            if "subject_visit" in [f.name for f in model._meta.get_fields()]:
                self.models.append(model)

    def has_crfs(
        self,
        subject_identifier,
        visit_code: str,
        visit_code_sequence: int,
    ):
        subject_visit = None
        try:
            subject_visit = self.subject_visit_model_cls.objects.get(
                subject_identifier=subject_identifier,
                visit_code=visit_code,
                visit_code_sequence=visit_code_sequence,
            )
        except ObjectDoesNotExist:
            pass
        except MultipleObjectsReturned:
            raise MultipleObjectsReturned("Specify the visit_code and visit_code_sequence")
        else:
            for model in self.models:
                if model.objects.filter(subject_visit=subject_visit).exists():
                    return subject_visit, True
        return subject_visit, False
