from django import forms
from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
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
