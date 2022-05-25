from datetime import date, datetime

from django import forms
from django.apps import apps as django_apps
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from edc_constants.constants import HIV, YES
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
    if is_baseline(instance=subject_visit):
        model_exists_or_raise(
            subject_visit=subject_visit,
            model_cls=get_clinical_review_baseline_model_cls(),
        )
    else:
        model_exists_or_raise(
            subject_visit=subject_visit, model_cls=get_clinical_review_model_cls()
        )


def raise_if_both_ago_and_actual_date(dx_ago: str, dx_date: date, cleaned_data=None) -> None:
    if cleaned_data:
        dx_ago = cleaned_data.get("dx_ago")
        dx_date = cleaned_data.get("dx_date")
    if dx_ago and dx_date:
        raise forms.ValidationError(
            {
                "dx_ago": (
                    "Date conflict. Do not provide a response "
                    "here if the exact data of diagnosis is available."
                )
            }
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


def medications_exists_or_raise(subject_visit) -> bool:
    if subject_visit:
        try:
            get_medication_model_cls().objects.get(subject_visit=subject_visit)
        except ObjectDoesNotExist:
            raise forms.ValidationError(
                f"Complete the `{get_medication_model_cls()._meta.verbose_name}` CRF first."
            )
    return True


def art_initiation_date(subject_identifier: str, report_datetime: datetime) -> date:
    """Returns date initiated on ART or None by querying
    the HIV Initial Review and then the HIV Review.
    """
    art_date = None
    try:
        initial_review = get_initial_review_model_cls(HIV).objects.get(
            subject_visit__subject_identifier=subject_identifier,
            report_datetime__lte=report_datetime,
        )
    except ObjectDoesNotExist:
        pass
    else:
        if initial_review.arv_initiated == YES:
            art_date = initial_review.best_art_initiation_date
        else:
            for review in (
                get_review_model_cls(HIV)
                .objects.filter(
                    subject_visit__subject_identifier=subject_identifier,
                    report_datetime__lte=report_datetime,
                )
                .order_by("-report_datetime")
            ):
                if review.arv_initiated == YES:
                    art_date = review.arv_initiation_actual_date
                    break
    return art_date
