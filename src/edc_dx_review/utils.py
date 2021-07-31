from django import forms
from django.apps import apps as django_apps
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from edc_model.utils import model_exists_or_raise
from edc_visit_schedule.utils import is_baseline

EDC_DX_REVIEW_APP_LABEL = getattr(settings, "EDC_DX_REVIEW_APP_LABEL", "edc_dx_review")


class ModelNotDefined(Exception):
    pass


class BaselineModelError(Exception):
    pass


def get_list_model_app():
    return getattr(
        settings, "EDC_DX_REVIEW_LIST_MODEL_APP_LABEL", settings.LIST_MODEL_APP_LABEL
    )


def get_clinical_review_baseline_model_cls():
    return django_apps.get_model(f"{EDC_DX_REVIEW_APP_LABEL}.clinicalreviewbaseline")


def get_clinical_review_model_cls():
    return django_apps.get_model(f"{EDC_DX_REVIEW_APP_LABEL}.clinicalreview")


def get_medication_model_cls():
    return django_apps.get_model(f"{EDC_DX_REVIEW_APP_LABEL}.medications")


def get_initial_review_model_cls(prefix):
    return django_apps.get_model(f"{EDC_DX_REVIEW_APP_LABEL}.{prefix.lower()}initialreview")


def get_review_model_cls(prefix):
    return django_apps.get_model(f"{EDC_DX_REVIEW_APP_LABEL}.{prefix.lower()}review")


def raise_if_clinical_review_does_not_exist(subject_visit) -> None:
    if is_baseline(subject_visit):
        model_exists_or_raise(
            subject_visit=subject_visit,
            model_cls=get_clinical_review_baseline_model_cls(),
        )
    else:
        model_exists_or_raise(
            subject_visit=subject_visit, model_cls=get_clinical_review_model_cls()
        )


def requires_clinical_review_at_baseline(subject_visit):
    try:
        get_clinical_review_baseline_model_cls().objects.get(
            subject_visit__subject_identifier=subject_visit.subject_identifier
        )
    except ObjectDoesNotExist:
        raise forms.ValidationError(
            "Please complete the "
            f"{get_clinical_review_baseline_model_cls()._meta.verbose_name} first."
        )


def raise_if_initial_review_does_not_exist(subject_visit, prefix):
    model_exists_or_raise(
        subject_visit=subject_visit,
        model_cls=get_initial_review_model_cls(prefix),
    )


def raise_if_review_does_not_exist(subject_visit, prefix):
    model_exists_or_raise(
        subject_visit=subject_visit,
        model_cls=get_review_model_cls(prefix),
    )
