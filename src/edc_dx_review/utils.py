from __future__ import annotations

from datetime import date, datetime

from django import forms
from django.apps import apps as django_apps
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from edc_constants.constants import HIV, YES
from edc_model.utils import model_exists_or_raise
from edc_visit_schedule.baseline import VisitScheduleBaselineError
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
    clinicalreviewbaseline = get_extra_attrs().get(
        "clinicalreviewbaseline", "clinicalreviewbaseline"
    )

    return django_apps.get_model(f"{EDC_DX_REVIEW_APP_LABEL}.{clinicalreviewbaseline}")


def get_clinical_review_model_cls():
    clinicalreview = get_extra_attrs().get("clinicalreview", "clinicalreview")
    return django_apps.get_model(f"{EDC_DX_REVIEW_APP_LABEL}.{clinicalreview}")


def get_medication_model_cls():
    medications = get_extra_attrs().get("medications", "medications")
    return django_apps.get_model(f"{EDC_DX_REVIEW_APP_LABEL}.{medications}")


def get_initial_review_model_cls(prefix):
    initialreview = get_extra_attrs().get("initialreview", "initialreview")
    return django_apps.get_model(f"{EDC_DX_REVIEW_APP_LABEL}.{prefix.lower()}{initialreview}")


def get_review_model_cls(prefix):
    review = get_extra_attrs().get("review", "review")
    return django_apps.get_model(f"{EDC_DX_REVIEW_APP_LABEL}.{prefix.lower()}{review}")


def get_extra_attrs():
    """Settings from EDC_DX_REVIEW_EXTRA_ATTRS.

    See model name suffixes used in model_cls getters in utils.py.
    """
    extra_attrs = {
        "clinicalreview": "clinicalreview",
        "clinicalreviewbaseline": "clinicalreviewbaseline",
        "initialreview": "initialreview",
        "medications": "medications",
        "review": "review",
    }
    try:
        data = getattr(settings, "EDC_DX_REVIEW_EXTRA_ATTRS")
    except AttributeError:
        pass
    else:
        extra_attrs.update(data)
    return extra_attrs


def raise_if_clinical_review_does_not_exist(subject_visit) -> None:
    try:
        baseline = is_baseline(instance=subject_visit)
    except VisitScheduleBaselineError as e:
        raise forms.ValidationError(str(e))
    else:
        if baseline:
            model_cls = get_clinical_review_baseline_model_cls()
        else:
            model_cls = get_clinical_review_model_cls()
        try:
            model_exists_or_raise(subject_visit=subject_visit, model_cls=model_cls)
        except ObjectDoesNotExist:
            raise forms.ValidationError(f"Complete {model_cls._meta.verbose_name} CRF first.")


def raise_if_both_ago_and_actual_date(
    cleaned_data: dict | None = None,
    date_fld: str | None = None,
    ago_fld: str | None = None,
    dx_ago: str | None = None,
    dx_date: date | None = None,
) -> None:
    if cleaned_data:
        dx_ago = cleaned_data.get(date_fld)
        dx_date = cleaned_data.get(ago_fld)
    if dx_ago and dx_date:
        raise forms.ValidationError(
            {
                ago_fld: (
                    "Date conflict. Do not provide a response "
                    "here if the date of diagnosis is available."
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


def is_rx_initiated(
    subject_identifier: str, report_datetime: datetime, instance_id: str | None = None
) -> bool:
    """Return True if already initiated"""
    try:
        get_initial_review_model_cls(HIV).objects.get(
            subject_visit__subject_identifier=subject_identifier,
            report_datetime__lte=report_datetime,
            rx_init=YES,
        )
    except ObjectDoesNotExist:
        exclude = {}
        if instance_id:
            exclude = {"id": instance_id}
        rx_initiated = (
            get_review_model_cls(HIV)
            .objects.filter(
                subject_visit__subject_identifier=subject_identifier,
                report_datetime__lte=report_datetime,
                rx_init=YES,
            )
            .exclude(**exclude)
            .exists()
        )
    else:
        rx_initiated = True
    return rx_initiated


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
