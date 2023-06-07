from django import forms
from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from edc_model import model_exists_or_raise


def raise_if_crf_does_not_exist(subject_visit, model: str) -> None:
    model_cls = django_apps.get_model(model)
    try:
        model_exists_or_raise(subject_visit=subject_visit, model_cls=model_cls)
    except ObjectDoesNotExist:
        raise forms.ValidationError(f"Complete {model_cls._meta.verbose_name} CRF first.")
